# -*- coding: utf-8 -*-


import scrapy
import json, re, time
from datetime import datetime
from ..items import InsphotoItem
from ..settings import INSTAGRAMMER


class InsSpider(scrapy.Spider):
    name = 'Ins'
    allowed_domains = ['instagram.com']

    # search target
    instagrammer = INSTAGRAMMER
    # urls
    url_index = 'https://www.instagram.com/%s/'
    url_js_zh = 'https://www.instagram.com/static/bundles/zh_CN_ConsumerCommons.js/%s.js'
    url_js = 'https://www.instagram.com/static/bundles/ConsumerCommons.js/%s.js'
    url_data = 'https://www.instagram.com/graphql/query/?query_id=%s&variables={"id":"%s","first":%s}'
    url_data_tail = ',"after":"%s"}'
    url_detail = 'https://www.instagram.com/p/%s/?taken-by=%s'
    start_url = url_index % instagrammer

    is_increment = False
    increment_sleep = 60
    information = {
        'query_id': None,
        'id': None,
        'first': None,
        'after': None,
        'latest': None,   # latest post's release date
        'cur_latest': None
    }


    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse_index)


    def parse_index(self, response):
        # parse json
        raw_json = response.xpath('//script/text()').re(r'window._sharedData = (.+);')[0]
        cooked_json = json.loads(raw_json)
        raw_data = cooked_json['entry_data']['ProfilePage'][0]['user']
        # 2 situations
        if self.is_increment:
            # is there new images?
            cur_latest = raw_data['media']['nodes'][0]['date']
            if cur_latest > self.information['latest']:
                self.__class__.information['cur_latest'] = cur_latest
        else:
            # fetch data
            self.__class__.information['id'] = raw_data['id']
            self.__class__.information['first'] = 100
            self.__class__.information['after'] = raw_data['media']['page_info']['end_cursor']
            self.__class__.information['latest'] = raw_data['media']['nodes'][0]['date']
            self.__class__.information['cur_latest'] = self.information['latest']
        if not self.is_increment or self.information['cur_latest'] > self.information['latest']:
            # for parsing javascript to get newest query_id
            zh = True
            js_name = response.xpath('//script/@src').re(r'zh_CN_ConsumerCommons\.js/(.+)\.js')
            if len(js_name) == 0:
                js_name = response.xpath('//script/@src').re(r'ConsumerCommons\.js/(.+)\.js')[0]
                zh = False
            else:
                js_name = js_name[0]
            js_url = self.url_js_zh % (js_name) if zh else self.url_js % (js_name)
            yield scrapy.Request(url=js_url, callback=self.parse_js, dont_filter=True)
        else:
            time.sleep(self.increment_sleep)
            print('____________________ finding new images')
            yield scrapy.Request(url=self.start_url, callback=self.parse_index, dont_filter=True)


    def parse_js(self, response):
        # find the query_id
        p = r'profilePosts\.byUserId\.get\(\w+\)\.pagination},queryId:"(\d+)"'
        self.__class__.information['query_id'] = re.search(p, response.text).group(1)
        # combine
        info = self.information
        data_url = self.url_data % (info['query_id'], info['id'], info['first'])
        yield scrapy.Request(url=data_url, callback=self.parse_data, dont_filter=True)


    def parse_data(self, response):
        increment_next_page = True
        # parse json
        raw_json = response.xpath('//pre/text()').extract_first()
        cooked_json = json.loads(raw_json)
        raw_data = cooked_json['data']['user']['edge_owner_to_timeline_media']
        edges = raw_data['edges']
        # fetch data
        for node in edges:
            node = node['node']
            if not node['is_video']:
                # incremental opration
                date = node['taken_at_timestamp']
                if self.is_increment and date <= self.information['latest']:
                    self.__class__.information['latest'] = self.information['cur_latest']
                    increment_next_page = False
                    break
                # fetch data
                item = InsphotoItem()
                item['url'] = node['display_url']
                item['like'] = node['edge_media_preview_like']['count']
                if not node['comments_disabled']:
                    item['comment'] = node['edge_media_to_comment']['count']
                else:
                    item['comment'] = 0
                item['detail'] = self.url_detail % (node['shortcode'], self.instagrammer)
                item['date'] = str(datetime.fromtimestamp(date))
                yield item
        # crawl next page, only in incremental situation increment_next_page can be false
        if raw_data['page_info']['has_next_page'] and increment_next_page:
            self.__class__.information['after'] = raw_data['page_info']['end_cursor']
            info = self.information
            data_url = (self.url_data[:-1]+self.url_data_tail)
            data_url = data_url % (info['query_id'], info['id'], info['first'], info['after'])
            yield scrapy.Request(url=data_url, callback=self.parse_data, dont_filter=True)
        elif increment_next_page == False:
            yield scrapy.Request(url=self.start_url, callback=self.parse_index, dont_filter=True)
        else:
            self.__class__.is_increment = True
            print('__________ start incremental crawling __________')
            yield scrapy.Request(url=self.start_url, callback=self.parse_index, dont_filter=True)
