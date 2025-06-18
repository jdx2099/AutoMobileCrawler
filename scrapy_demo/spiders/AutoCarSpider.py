import os
import scrapy
import re
import csv  # 添加csv模块导入
import time  # 添加time模块用于时间统计
from scrapy import cmdline
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy_demo.items import AutoCarListItem
from w3lib.html import remove_tags, replace_escape_chars
import threading

class autocarSpider(scrapy.Spider):
    name = "AutoCarSpider" # 爬虫名称，用于区分不同的爬虫
    allowed_domains = ['12365auto.com'] # 允许爬取的域名列表
    # 自定义设置，用于配置输出文件的格式和路径，以及是否覆盖已存在的文件
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    custom_settings = {
        'FEEDS': {
             os.path.join(output_dir, 'AutoCarSpider-Output.csv'): {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': ['brand_id','brand_name','series_name','vehicle_id','car_name','car_url','vehicle_style','zlts_id','zlts_url','full_review'],
                'overwrite': False,
                'append': True
            }
        },
        'ITEM_PIPELINES': {
            'scrapy_demo.pipelines.DataCleaningPipeline':200,
            'scrapy_demo.pipelines.CsvToJsonPipelineutf8':300
        }
    }
    # 初始化方法，用于设置爬虫的起始URL和车系名称
    def __init__(self, car_name=None, api_response=None, *args, **kwargs):
        super(autocarSpider, self).__init__(*args, **kwargs)
        self.car_name = car_name
        self.collected_items = []  # 添加数据收集列表
        self.existing_zlts_urls = set()
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        csv_file = os.path.join(output_dir, 'AutoCarSpider-Output.csv')
        data = []  # 初始化data为空列表
        if os.path.exists(csv_file):
            for encoding in ['utf-8', 'gbk', 'gb18030']:
                try:
                    with open(csv_file, 'r', newline='', encoding=encoding,errors='ignore') as f:
                        reader = csv.DictReader(f, fieldnames=['brand_id','brand_name','series_name','vehicle_id','car_name','car_url','vehicle_style','zlts_id','zlts_url','full_review'])
                        data = list(reader)
                        break
                except UnicodeDecodeError:
                    continue
        for item in data:
            zlts_url = item.get('zlts_url')
            if zlts_url:
                self.existing_zlts_urls.add(zlts_url)
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
    def parse(self, response):
        # ... 解析逻辑 ...
        self.collected_items.append(item)  # 收集数据
    # 解析车型列表页面的方法，用于提取车型名称和对应的URL
    def parse_car(self,response): 
        selector = Selector(response) # 解析响应内容
        car_name=self.car_name  # 使用传入的参数
        if car_name:
            # 提取车型投诉的链接
            series_href= response.xpath(f'//div[b/a[normalize-space(text())="{car_name}"]]/span/a[1]/@href').get()
            if series_href:
                brand_id=response.xpath(f'//div[b/a[normalize-space(text())="{car_name}"]]/../../../../..//@data-id').get().strip()
                brand_name=response.xpath(f'//div[b/a[normalize-space(text())="{car_name}"]]/../../../../..//div[@class="left"]/dl/dd/a/text()').get().strip()
                car_url = response.urljoin(series_href) # 构建完整的URL 
                #self.logger.info(f"{brand_name}的ID为{brand_id}")
                vehicle_id = re.search(r'series/c-(\d+)', car_url).group(1)
                # 发送请求到车型投诉页面，设置回调函数和元数据
                yield scrapy.Request(car_url, 
                            callback=self.parse_zlts_review,
                            meta={
                                'brand_id':brand_id,
                                'brand_name':brand_name,
                                'vehicle_id':vehicle_id,
                                'car_name':car_name,
                                'car_url': car_url
                            })
            else:
                self.logger.error(f"未找到车系名称为 {car_name} 的链接")
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
                zlts_id = re.search(r'zlts/\d+/(\d+)\.shtml', zlts_url).group(1)# 检查 zlts_url 是否已经存在
                # 发送请求到具体投诉内容页面，设置回调函数和元数据
                if zlts_url not in self.existing_zlts_urls:
                    self.existing_zlts_urls.add(zlts_url)
                    yield scrapy.Request(zlts_url,
                                        callback=self.parse_zlts_detail,
                                        meta={
                                            **response.meta,
                                            'zlts_id':zlts_id,
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
    def parse_zlts_detail(self, response):
        selector = Selector(response)
        series_name = selector.xpath('//div[@class="jbqk"]/ul/li[3]/text()').get().strip()
        car_name = selector.xpath('//div[@class="jbqk"]/ul/li[4]/text()').get().strip()
        vehicle_style= selector.xpath('//div[@class="jbqk"]/ul/li[5]/text()').get().strip()
        full_review = replace_escape_chars(remove_tags(selector.xpath('//div[@class="tsnr"]/p/text()').get()))
        item = AutoCarListItem()
        item['brand_id']= response.meta['brand_id']
        item['brand_name'] = response.meta['brand_name']
        item['series_name'] = series_name
        item['vehicle_id']= response.meta['vehicle_id']
        item['car_name'] = car_name
        item['car_url'] = response.meta['car_url']
        item['vehicle_style'] = vehicle_style
        item['zlts_id']= response.meta['zlts_id']
        item['zlts_url'] = response.meta['zlts_url']
        item['full_review'] = full_review
            
        self.collected_items.append(item)  # 收集数据
        yield item

if __name__ == "__main__":
    # 当脚本作为主程序运行时执行的代码
    from scrapy.crawler import CrawlerRunner
    # 导入CrawlerRunner类，用于运行Scrapy爬虫
    
    from scrapy.utils.project import get_project_settings
    # 导入get_project_settings函数，用于获取Scrapy项目配置
    
    from twisted.internet import reactor
    # 导入Twisted的reactor，用于事件循环
    
    settings = get_project_settings()
    # 获取当前Scrapy项目的配置设置
    
    runner = CrawlerRunner(settings)
    # 创建CrawlerRunner实例，传入项目配置
    
    runner.crawl(AutoCarSpider, car_name="奥迪Q6")
    # 启动AutoCarSpider爬虫，并传入参数car_name="奥迪Q6"
    
    def stop_reactor():
        reactor.stop()
    # 定义停止reactor的函数
    
    reactor.addSystemEventTrigger('before', 'shutdown', stop_reactor)
    # 在系统关闭前注册回调函数stop_reactor
    
    reactor.run()
    # 启动Twisted reactor事件循环