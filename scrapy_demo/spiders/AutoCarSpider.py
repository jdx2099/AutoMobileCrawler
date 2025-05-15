import scrapy
from scrapy import cmdline
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy_demo.items import AutoSpiderItem
from w3lib.html import remove_tags, replace_escape_chars
import os

class autocarSpider(scrapy.Spider): 
    name = "AutoCarSpider" # 爬虫名称，用于区分不同的爬虫
    allowed_domains = ['12365auto.com'] # 允许爬取的域名列表
    # 自定义设置，用于配置输出文件的格式和路径，以及是否覆盖已存在的文件
    #output_dir = 'E:/ScrapyProject/AutoCarScrapy/scrapy_demo/output/'
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    custom_settings = {
        'FEEDS': {
            f'{output_dir}/%(name)s-Output.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': ['brand_name','series_name','car_name','car_url','zlts_url','full_review'],
                'overwrite': True
            }
        }
    }
    # 初始化方法，用于设置爬虫的起始URL和车系名称
    def __init__(self, series_name=None, *args, **kwargs):
        super(autocarSpider, self).__init__(*args, **kwargs)
        self.series_name = series_name
        self.start_urls = [f'https://www.12365auto.com/list/models.shtml'] 

    # 当爬虫启动时，会调用该方法，用于发送初始请求
    def start_requests(self):
        url = 'https://www.12365auto.com/list/models.shtml' # 车质网车型列表页面
        # 发送请求到车质网车型列表页面，设置请求头和错误处理回调函数
        yield scrapy.Request(url,
                callback=self.parse_car,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                errback=self.handle_error
            )
    # 错误处理回调函数，用于处理请求失败的情况
    def handle_error(self, failure):
        self.logger.error(repr(failure))

    # 解析车型列表页面的方法，用于提取车型名称和对应的URL
    def parse_car(self,response): 
        selector = Selector(response) # 解析响应内容
        series_name=self.series_name  # 使用传入的参数
        if series_name:
            # 提取车型投诉的链接
            series_href= response.xpath(f'//div[b/a[normalize-space(text())="{series_name}"]]/span/a[1]/@href').get()
            if series_href:
                car_url = response.urljoin(series_href) # 构建完整的URL
                # 发送请求到车型投诉页面，设置回调函数和元数据
                yield scrapy.Request(car_url, 
                            callback=self.parse_zlts_review,
                            meta={
                                'series_name': series_name,
                                'car_url': car_url
                            })
            else:
                self.logger.error(f"未找到车系名称为 {series_name} 的链接")
        else:
            self.logger.error("未提供车系名称")
    
    # 解析车型投诉页面的方法，用于提取具体投诉内容页面的URL
    def parse_zlts_review(self,response):
        # 检查meta数据是否存在，如果不存在则打印错误日志并返回
        if 'car_url' not in response.meta:
            self.logger.error("Missing meta data in response: %s", response.url)
            return
        selector = Selector(response) # 解析响应内容
        # 提取所有具体投诉内容页面的链接，使用getall()方法获取所有匹配的元素
        zlts_urls = selector.xpath('//td[@class="tsjs"]/a/@href').getall()
        # 若当前页面存在投诉信息
        if zlts_urls:
            # 遍历每个具体投诉内容页面的链接，构建完整的URL，并发送请求到具体投诉内容页面
            for zlts_url in zlts_urls:
                zlts_url = response.urljoin(zlts_url) # 构建完整的URL
                # 发送请求到具体投诉内容页面，设置回调函数和元数据
                yield scrapy.Request(zlts_url,
                                    callback=self.parse_zlts_detail,
                                    meta={
                                        **response.meta,
                                        'zlts_url': zlts_url
                                    })
            # 处理下一页，抓取下一页的url，并更新meta参数中的car_url
            next_page = selector.xpath('//div[@class="p_page"]/a[text()="下一页"]/@href').get()
            # 如果存在下一页，构建完整的URL，并发送请求到下一页
            if next_page:
                next_page_url = response.urljoin(next_page)
                # 更新meta参数中的car_url为下一页的url
                yield scrapy.Request(next_page_url,
                                        callback=self.parse_zlts_review, 
                                        meta={
                                            **response.meta,
                                            'car_url': next_page_url # 仅更新car_url
                                    })

    # 解析具体投诉内容页面的方法，用于提取车型名称、车系名称、车型名称和完整的投诉内容
    def parse_zlts_detail(self,response):
        selector = Selector(response) # 解析响应内容
        # 提取车型名称、车系名称、车型名称和完整的投诉内容
        brand_name = selector.xpath('//div[@class="jbqk"]/ul/li[3]/text()').get().strip()
        car_name = selector.xpath('//div[@class="jbqk"]/ul/li[5]/text()').get().strip()
        full_review=replace_escape_chars(remove_tags(selector.xpath('//div[@class="tsnr"]/p/text()').get()))
        
        item = AutoSpiderItem() # 创建一个AutoSpiderItem对象，用于存储爬取的数据
        # 将提取到的数据存储到AutoSpiderItem对象中
        item['brand_name'] = brand_name
        item['series_name'] = response.meta['series_name']
        item['car_name'] = car_name
        item['car_url'] = response.meta['car_url']
        item['zlts_url'] = response.meta['zlts_url']
        item['full_review'] = full_review
        yield item

# 主函数，用于启动爬虫
if __name__ == "__main__":
    # 检查当前模块是否作为主程序运行
    process = CrawlerProcess()
    # 创建一个CrawlerProcess实例，用于启动和管理爬虫
    process.crawl(AutoCarSpider)
    # 将AutoCarSpider爬虫添加到进程中
    process.start()
    # 启动爬虫进程