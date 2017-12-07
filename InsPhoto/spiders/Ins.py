# -*- coding: utf-8 -*-


import scrapy
import json, re


class InsSpider(scrapy.Spider):
    name = 'Ins'

    allowed_domains = ['instagram.com']
    url_index = 'https://www.instagram.com/%s/'
    url_js = 'https://www.instagram.com/static/bundles/zh_CN_ConsumerCommons.js/%s.js'
    url_data = 'https://www.instagram.com/graphql/query/?query_id=%s&variables={"id":"%s","first":%s,"after":"%s"}'

    # search target
    instagrammer = 'ahmad_monk'
    information = {
        # for url_data
        'query_id': None,
        'id': None,
        'first': None,
        'after': None,
        # for incremental crawler
        'posts': None,    # number of posts
        'latest': None    # latest post's release date
    }

    def start_requests(self):
        start_url = self.url_index % (self.instagrammer)
        yield scrapy.Request(url=start_url, callback=self.parse_index)

    def parse_index(self, response):
        # parse json
        raw_json = response.xpath('//script/text()').re(r'window._sharedData = (.+);')[0]
        cooked_json = json.loads(raw_json)
        raw_data = cooked_json['entry_data']['ProfilePage'][0]['user']
        # fetch data
        self.__class__.information['id'] = raw_data['id']
        self.__class__.information['first'] = 12
        self.__class__.information['after'] = raw_data['media']['page_info']['end_cursor']
        self.__class__.information['posts'] = raw_data['media']['count']
        self.__class__.information['latest'] = raw_data['media']['nodes'][0]['date']
        # for parsing javascript to find query_id
        js_name = response.xpath('//script/@src').re(r'zh_CN_ConsumerCommons\.js/(.+)\.js')[0]
        js_url = self.url_js % (js_name)
        yield scrapy.Request(url=js_url, callback=self.parse_js)

    def parse_js(self, response):
        # find the query_id
        p = r'profilePosts\.byUserId\.get\(\w+\)\.pagination},queryId:"(\d+)"'
        self.__class__.information['query_id'] = re.search(p, response.text).group(1)
        # combine
        info = self.information
        data_url = self.url_data % (info['query_id'], info['id'], info['first'], info['after'])
        yield scrapy.Request(url=data_url, callback=self.parse_data)

    def parse_data(self, response):
        # parse json
        raw_json = response.xpath('//pre/text()').extract_first()
        cooked_json = json.loads(raw_json)
        raw_data = cooked_json['data']['user']['edge_owner_to_timeline_media']
        # fetch data
        self.__class__.information['after'] = raw_data['page_info']['end_cursor']
        has_next_page = raw_data['page_info']['has_next_page']
        edges = raw_data['edges']
        # fetch items
        for node in edges:
            pass
