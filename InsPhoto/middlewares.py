# -*- coding: utf-8 -*-


import time
from selenium import webdriver
from scrapy.http import HtmlResponse
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

class InsPhotoDownloaderMiddleware(object):
    @classmethod
    def process_request(cls, request, spider):
        HEADLESS_BROWSER = webdriver.PhantomJS()
        HEADLESS_BROWSER.get(request.url)
        print('____________________ downloding page')
        time.sleep(3)
        body = HEADLESS_BROWSER.page_source
        HEADLESS_BROWSER.quit()
        print('____________________ page dowmloded ')
        return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
