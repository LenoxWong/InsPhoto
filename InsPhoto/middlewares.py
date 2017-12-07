# -*- coding: utf-8 -*-


import time
from selenium import webdriver
from scrapy.http import HtmlResponse


class InsPhotoDownloaderMiddleware(object):
    @classmethod
    def process_request(cls, request, spider):
        HEADLESS_BROWSER = webdriver.PhantomJS()
        HEADLESS_BROWSER.get(request.url)
        time.sleep(1)
        body = HEADLESS_BROWSER.page_source
        HEADLESS_BROWSER.quit()
        return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
