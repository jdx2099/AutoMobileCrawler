BOT_NAME = 'scrapy_demo'
SPIDER_MODULES = ['scrapy_demo.spiders']
# Obey robots.txt rules
ROBOTSTXT_OBEY =False # 这里改成False，表示不遵守robots协议
# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}  # 然后把这个放开，这个表示该项目的默认请求头

# 修改管道配置
ITEM_PIPELINES = {
    'scrapy_demo.pipelines.DataCleaningPipeline':300,
#    'scrapy_demo.pipelines.OptionValidationPipeline': 300,  # 注释掉不存在的管道
#    'scrapy_demo.pipelines.MongoDBPipeline': 800,

    #'parkers.pipelines.DataValidationPipeline': 400,
}
# 动态输出路径（使用爬虫名作为文件名部分）
import os
output_dir = 'E:/ScrapyProject/AutoCarScrapy/scrapy_demo/output/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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
CONCURRENT_REQUESTS = 64

# The download delay setting will honor only one of:
# 单域名和单IP并发数，会覆盖上面的设定
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# 对爬虫进行监控
#TELNETCONSOLE_ENABLED = False
# TELNETCONSOLE_ENABLED = True
# TELNETCONSOLE_HOST = '127.0.0.1'
# TELNETCONSOLE_PORT = [6023,]
# 操作命令：cmd -> telent 127.0.0.1 6023-> est<>
# 增加重试机制和超时设置
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408,429]
DOWNLOAD_TIMEOUT = 60
DOWNLOAD_DELAY = 1.5  # 添加2秒下载延迟
# 启用自动限速
'''
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
'''