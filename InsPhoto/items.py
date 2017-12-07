# -*- coding: utf-8 -*-


import scrapy


class InsphotoItem(scrapy.Item):
    url = scrapy.Field()
    like = scrapy.Field()
    comment = scrapy.Field()
    date = scrapy.Field()
    detail = scrapy.Field()
