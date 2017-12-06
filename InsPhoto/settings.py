# -*- coding: utf-8 -*-


BOT_NAME = 'InsPhoto'

SPIDER_MODULES = ['InsPhoto.spiders']
NEWSPIDER_MODULE = 'InsPhoto.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 3

COOKIES_ENABLED = True

TELNETCONSOLE_ENABLED = True

DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'zh-CN,zh;q=0.9',
}

DOWNLOADER_MIDDLEWARES = {
   'InsPhoto.middlewares.InsPhotoDownloaderMiddleware': 901,
}

ITEM_PIPELINES = {
   'InsPhoto.pipelines.InsphotoPipeline': 300,
}
