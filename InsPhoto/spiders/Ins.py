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
# ...
# ...
# ...
# 2017-12-08 21:32:18 [scrapy.core.scraper] DEBUG: Scraped from <200 https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=%7B%22id%22:%2222543622%22,%22first%22:100,%22after%22:%22AQAWqcYrUaowXHBS3TM3Aajj5JLPW5x_hky7__LmDKYp3nu4UPY9jh8iiKkEWkCTn1SLO2iUxjn32HnZww2YOAH7KwIDNwnOEU7QpjkgA_obvQ%22%7D>
# {'comment': 36,
#  'date': '2013-07-30 06:47:59',
#  'detail': 'https://www.instagram.com/p/cXf-UtOJ3B/?taken-by=ahmad_monk',
#  'like': 465,
#  'url': 'https://scontent-nrt1-1.cdninstagram.com/t51.2885-15/e15/11275320_790115737773242_601775010_n.jpg'}
# 2017-12-08 21:32:18 [scrapy.core.scraper] DEBUG: Scraped from <200 https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=%7B%22id%22:%2222543622%22,%22first%22:100,%22after%22:%22AQAWqcYrUaowXHBS3TM3Aajj5JLPW5x_hky7__LmDKYp3nu4UPY9jh8iiKkEWkCTn1SLO2iUxjn32HnZww2YOAH7KwIDNwnOEU7QpjkgA_obvQ%22%7D>
# {'comment': 20,
#  'date': '2013-06-28 03:36:25',
#  'detail': 'https://www.instagram.com/p/bEwnSROJ1L/?taken-by=ahmad_monk',
#  'like': 397,
#  'url':  'https://scontent-nrt1-1.cdninstagram.com/t51.2885-15/e15/11203431_427708267409977_313556750_n.jpg'}
# ...
# ...
# ...
# __________ start incremental crawling __________
# ____________________ downloding page
# ____________________ page dowmloded
# 2017-12-08 21:33:18 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.instagram.com/ahmad_monk/> (referer: https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=%7B%22id%22:%2222543622%22,%22first%22:100,%22after%22:%22AQAWqcYrUaowXHBS3TM3Aajj5JLPW5x_hky7__LmDKYp3nu4UPY9jh8iiKkEWkCTn1SLO2iUxjn32HnZww2YOAH7KwIDNwnOEU7QpjkgA_obvQ%22%7D)
# 2017-12-08 21:33:18 [scrapy.extensions.logstats] INFO: Crawled 6 pages (at 5 pages/min), scraped 238 items (at 238 items/min)
# ____________________ finding new images
# 2017-12-08 21:34:18 [scrapy.extensions.logstats] INFO: Crawled 6 pages (at 0 pages/min), scraped 238 items (at 0 items/min)
# ____________________ downloding page
# ____________________ page dowmloded
# 2017-12-08 21:34:31 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.instagram.com/ahmad_monk/> (referer: https://www.instagram.com/ahmad_monk/)
# ____________________ finding new images
# 2017-12-08 21:35:31 [scrapy.extensions.logstats] INFO: Crawled 7 pages (at 1 pages/min), scraped 238 items (at 0 items/min)
# ____________________ downloding page
# ____________________ page dowmloded
# ...
# ...
# ...
# ^C2017-12-08 21:36:26 [scrapy.crawler] INFO: Received SIG_UNBLOCK, shutting down gracefully. Send again to force
# ____________________ finding new images
# 2017-12-08 21:36:40 [scrapy.core.engine] INFO: Closing spider (shutdown)
# 2017-12-08 21:36:40 [scrapy.extensions.logstats] INFO: Crawled 8 pages (at 0 pages/min), scraped 238 items (at 0 items/min)
# 2017-12-08 21:36:40 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
# {'finish_reason': 'shutdown',
#  'finish_time': datetime.datetime(2017, 12, 8, 13, 36, 40, 305107),
#  'item_scraped_count': 238,
#  'log_count/DEBUG': 247,
#  'log_count/INFO': 14,
#  'memusage/max': 76636160,
#  'memusage/startup': 63647744,
#  'request_depth_max': 8,
#  'response_received_count': 8,
#  'scheduler/dequeued': 8,
#  'scheduler/dequeued/memory': 8,
#  'scheduler/enqueued': 9,
#  'scheduler/enqueued/memory': 9,
#  'start_time': datetime.datetime(2017, 12, 8, 13, 30, 37, 621036)}
# 2017-12-08 21:36:40 [scrapy.core.engine] INFO: Spider closed (shutdown)
