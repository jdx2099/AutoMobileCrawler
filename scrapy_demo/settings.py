BOT_NAME = 'scrapy_demo'
SPIDER_MODULES = ['scrapy_demo.spiders']
# Obey robots.txt rules
ROBOTSTXT_OBEY = False # 这里改成False，表示不遵守robots协议
# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}  # 然后把这个放开，这个表示该项目的默认请求头

# 修改管道配置
ITEM_PIPELINES = {
    'scrapy_demo.pipelines.DataCleaningPipeline':300,
}
# settings.py 激活中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy_demo.middlewares.CustomRetryMiddleware': 200,
    'scrapy_demo.middlewares.RandomUserAgentMiddleware': 220,
}
# 动态输出路径（使用爬虫名作为文件名部分）
import os
output_dir = 'E:/Documents/ScrapyProject/scrapy_demo/scrapy_demo/output/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
#默认配置
'''
FEEDS = {
    f'{output_dir}/%(name)s-Output.csv': {
        'format': 'csv',
        'encoding': 'utf8',
        'fields': (
            ['brand_name','series_name','car_name','car_url','zlts_url','full_review']
            #['brand_name','brand_url','series_name','series_url','car_name','car_url','car_type','zlts_url','score','full_review']
        ),
        'overwrite': True
    }
}
'''
ADDONS = {
    "scrapy_poet.Addon": 300,
}
LOG_ENABLED = True
LOG_FILE = 'Scrapy.log'
#LOG_LEVEL = 'DEBUG'
LOG_LEVEL = 'INFO'
#LOG_LEVEL = 'WARNING'
#LOG_LEVEL = 'ERROR'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# 增加以下配置项
# 并发请求数
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 100 # 增加并发请求数
# The download delay setting will honor only one of:
# 单域名和单IP并发数，会覆盖上面的设定
#CONCURRENT_REQUESTS_PER_DOMAIN = 64
#CONCURRENT_REQUESTS_PER_IP = 50

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# 对爬虫进行监控
#TELNETCONSOLE_ENABLED = False
#TELNETCONSOLE_ENABLED = True
#TELNETCONSOLE_HOST = '127.0.0.1'
#TELNETCONSOLE_PORT = [6023,]
# 操作命令：cmd -> telent 127.0.0.1 6023-> est<>
# 增加重试机制和超时设置
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408,429]
DOWNLOAD_TIMEOUT = 40
DOWNLOAD_DELAY = 2

# 启用自动限速
AUTOTHROTTLE_ENABLED = False
'''
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
'''
# 统一设置全局编码
FEED_EXPORT_ENCODING = 'utf-8'
DEFAULT_REQUEST_HEADERS = {
    'Accept-Encoding': 'gzip, deflate',
}