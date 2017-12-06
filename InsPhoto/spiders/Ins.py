# -*- coding: utf-8 -*-
import scrapy


class InsSpider(scrapy.Spider):
    name = 'Ins'
    allowed_domains = ['www.instagram.com']
    start_urls = ['http://www.instagram.com/']

    def parse(self, response):
        print('---------- spider is running ----------')
