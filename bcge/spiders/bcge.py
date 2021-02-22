import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bcge.items import Article


class BcgeSpider(scrapy.Spider):
    name = 'bcge'
    start_urls = ['https://www.bcge.ch/fr/news']

    def parse(self, response):
        articles = response.xpath('//div[@class="list list--news"]')
        for article in articles:
            link = article.xpath('.//a[@class="list__link"]/@href').get()
            date = article.xpath('.//span[@class="list__date"]/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2[@class="hero__content-title"]/text()').get()
        if title:
            title = title.strip()

        if date:
            date = " ".join(date.split()[:-1]).strip()

        content = response.xpath('//div[@class="text-simple__description"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
