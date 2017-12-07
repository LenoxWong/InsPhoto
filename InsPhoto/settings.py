# -*- coding: utf-8 -*-


INSTAGRAMMER = 'ahmad_monk'
STOP_CRAWL = 24 # after this hours, spider stops

BOT_NAME = 'InsPhoto'

SPIDER_MODULES = ['InsPhoto.spiders']
NEWSPIDER_MODULE = 'InsPhoto.spiders'

# since dowmloder middlewares set to 100, this is not used
# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',

ROBOTSTXT_OBEY = False

# DOWNLOAD_DELAY = 3

# COOKIES_ENABLED = False

# TELNETCONSOLE_ENABLED = True

# since dowmloder middlewares set to 100, this is not used
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#   'Accept-Encoding': 'gzip, deflate, br',
#   'Accept-Language': 'zh-CN,zh;q=0.9',
# }

DOWNLOADER_MIDDLEWARES = {
   'InsPhoto.middlewares.InsPhotoDownloaderMiddleware': 100,
   'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
   'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': None,
   'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': None,
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
   'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
   'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
   'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': None,
   'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
   'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
   'scrapy.downloadermiddlewares.stats.DownloaderStats': None
}

ITEM_PIPELINES = {
   'InsPhoto.pipelines.InsphotoPipeline': 300,
}
