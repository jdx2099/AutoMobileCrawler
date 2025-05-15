import os
import scrapy
from scrapy import cmdline
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy_demo.items import AutoCarListItem
from w3lib.html import remove_tags, replace_escape_chars

class autocarList(scrapy.Spider): 
    name = "AutoCarList" # 爬虫名称，用于区分不同的爬虫
    allowed_domains = ['12365auto.com'] # 允许爬取的域名列表
    start_urls = [f'https://www.12365auto.com/'] # 初始爬取的URL列表
    
    #output_dir = 'E:/ScrapyProject/AutoCarScrapy/scrapy_demo/output/'
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    custom_settings = {
        'FEEDS': {
            f'{output_dir}/%(name)s-Output.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': ['brand_name','brand_url','series_name','series_url','car_name','car_url','car_type','zlts_url','score'],
                'overwrite': True
            }
        }
    }
    def start_requests(self): 
        url = 'https://www.12365auto.com/list/models.shtml' # 车质网车型列表页面
        # 发送请求到车质网车型列表页面，设置请求头和错误处理回调函数
        yield scrapy.Request(url,
                callback=self.parse_cars,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                errback=self.handle_error
            )
    # 错误处理回调函数，用于处理请求失败的情况
    def handle_error(self, failure):
        self.logger.error(repr(failure))

    def parse_cars(self,response): 
        selector = Selector(response) # 解析响应内容
        #brands = selector.xpath(f'//*[@id="A"]//*[@class="left"]/dl/dd/a')
        brands = selector.xpath(f'//*[@class="left"]/dl/dd/a')
        self.logger.info(f"该网站的车辆品牌共找到{len(brands)}个")  # 新增统计日志
        for brand in brands:
            # 提取车型投诉的链接，使用getall()方法获取所有匹配的元素    
            brand_name = brand.xpath('text()').get().strip()
            brand_url = response.urljoin(brand.xpath('@href').get())
            # 发送请求到车型投诉页面，设置回调函数和元数据
            yield scrapy.Request(brand_url, 
                        callback=self.parse_brand_review,
                        meta={
                            'brand_name': brand_name,
                            'brand_url': brand_url
                        })

    def parse_brand_review(self,response):
        # 检查meta数据是否存在，如果不存在则打印错误日志并返回
        if 'brand_url' not in response.meta:
            self.logger.error("Missing meta data in response: %s", response.url)
            return
        selector = Selector(response) # 解析响应内容
        # 提取所有具体投诉内容页面的链接，使用getall()方法获取所有匹配的元素
        series = selector.xpath('//*[@class="top-navs"]/dl/dt/a')
        # 遍历每个具体投诉内容页面的链接，构建完整的URL，并发送请求到具体投诉内容页面
        for serie in series:
            series_url = response.urljoin(serie.xpath('@href').get())
            series_name = serie.xpath('text()').get().strip()
            # 发送请求到具体投诉内容页面，设置回调函数和元数据
            yield scrapy.Request(series_url,
                                callback=self.parse_series_review,
                                meta={
                                    'brand_name': response.meta['brand_name'], # 保留原有brand_name
                                    'brand_url': response.meta['brand_url'], # 保留原有brand_url
                                    'series_url': series_url,
                                    'series_name': series_name
                                })
    
    def parse_series_review(self,response):
        selector = Selector(response) # 解析响应内容
        if 'brand_url' not in response.meta:
            self.logger.error("Missing brand_url in response meta: %s", response.url)
            return

        cars= selector.xpath('//*[@class="datacenter"]/div[2]//ul')
        for car in cars:
            car_name = car.xpath('li[1]/a/text()').get().strip() # 
            car_url = response.urljoin(car.xpath('li[1]/a/@href').get())
            car_type = car.xpath('li[3]/span[1]/i/text()').get().strip() # 
            zlts_url = response.urljoin(car.xpath('li[4]/a[2]/@href').get())
            score = car.xpath('li[1]/span[2]/b/text()').get().strip() # 新增的字段，用于存储车型分数
            item = AutoCarListItem() # 创建一个AutoCarListItem对象，用于存储爬取的数据
            # 将提取到的数据存储到AutoCarListItem对象中
            item['brand_name'] = response.meta['brand_name']
            item['brand_url'] = response.meta['brand_url']
            item['series_name'] = response.meta['series_name']
            item['series_url'] = response.meta['series_url']
            item['car_name'] = car_name
            item['car_url'] = car_url
            item['car_type']=car_type
            item['zlts_url'] = zlts_url
            item['score'] = score
            yield item # 将AutoCarListItem对象传递给引擎，引擎会将其传递给pipelines进行处理
        
        next_page_button = selector.xpath('//*[@class="p_page"]/a[text()="下一页"]')
        # 如果存在下一页，构建完整的URL，并发送请求到下一页
        if next_page_button:
            next_page = selector.xpath('//*[@class="p_page"]/a[text()="下一页"]/@href').get()
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url,
                                    callback=self.parse_series_review, 
                                    meta={
                                        **response.meta
                                })

    def spider_opened(self, spider):
        self.start_time = time.time()  # 仅执行一次的时间戳记录

    def spider_closed(self, spider):
        elapsed_time = time.time() - self.start_time  # 仅执行一次的时间计算

if __name__ == '__main__':

    cmdline.execute("scrapy crawl AutoCarList --nolog".split())