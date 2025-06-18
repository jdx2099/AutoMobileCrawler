from scrapy_demo.items import ScrapyDemoItem
from bs4 import BeautifulSoup
import requests
import time
import scrapy
import os
class ParkersCarSpider(scrapy.Spider):
    name = "ParkersCarSpider"
    allowed_domains = ['parkers.co.uk']
    start_urls = ["https://www.parkers.co.uk/"]
    # 自定义设置，用于配置输出文件的格式和路径，以及是否覆盖已存在的文件
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    custom_settings = {
        'FEEDS': {
            f'{output_dir}/%(name)s-Output.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': ['brand_name','brand_url','car_name','car_url','full_review_url','full_review'],
                'overwrite': True
            },
            f'{output_dir}/%(name)s-Output.json': {
                'format': 'json',
                'encoding': 'utf8',
                'fields': ['brand_name','brand_url','car_name','car_url','full_review_url','full_review'],
                'overwrite': True,
                'indent': 2,
                'ensure_ascii': False
            }
        }
    }
    # 初始化方法，用于设置爬虫的车系名称
    def __init__(self, car_name=None, *args, **kwargs):
        super(ParkersCarSpider,self).__init__(*args, **kwargs)
        self.car_name = car_name
        if not car_name:
            self.logger.warning("未提供car_name参数，将爬取所有车型")
        else:
            self.logger.info(f"将爬取车型名称包含'{car_name}'的车辆")

    def start_requests(self):
        url = 'https://www.parkers.co.uk/car-manufacturers/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        yield scrapy.Request(url,headers=headers, callback=self.parse_brand)

    def parse_brand(self, response):
        #self.logger.info(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        options = soup.select('#manufacturerSelectorPage li article h2 a')
        for opt in options:
            brand_name = opt.text.strip()
            brand_url = f'https://www.parkers.co.uk/{brand_name}/owner-reviews/'
            # 验证brand_url是否为404
            check_response = requests.head(brand_url)
            if check_response.status_code == 404:
                #self.logger.info(f"该网页: {brand_url}下无车辆评价，跳过！")
                continue
            elif check_response.status_code == 400:
                self.logger.info(f"{brand_url}为无效链接！")
                continue
            yield scrapy.Request(brand_url, callback=self.parse_car, meta={'brand_name': brand_name, 'brand_url': brand_url})

    def parse_car(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        car_name=self.car_name  # 使用传入的参数
        if car_name:
            #在售车辆中车辆名包含car_name的
            series_links = [link for link in soup.select('#latestModelsContainer h4 a') if car_name in link.get_text()]
            if series_links:
                for series_link in series_links:
                    brand_name = response.meta['brand_name']
                    brand_url = response.meta['brand_url']
                    car_name= series_link.get_text().replace('Owner Reviews', '').strip()
                    car_url = response.urljoin(series_link['href'])
                    yield scrapy.Request(car_url, callback=self.parse_series_review, meta={'brand_name': brand_name, 'brand_url': brand_url, 'car_name': car_name, 'car_url': car_url})

    def parse_series_review(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = soup.select('li.owner-review-list__item article>a')
        for href in urls:
            full_review_text = ''
            review_elements = href.find_parent('article').select('div:nth-child(2) > div:nth-child(2) p')
            if review_elements:
                full_review_text = review_elements[0].get_text(strip=True)
            if full_review_text:
                full_review_url = response.urljoin(href['href'])
                yield scrapy.Request(full_review_url, callback=self.parse_full_review, meta={**response.meta, 'full_review_url': full_review_url})
        next_buttons = soup.select('.results-paging__next__link')
        if next_buttons:
            next_page = response.urljoin(next_buttons[0]['href'])
            #self.logger.info(f"Next Page: {next_page}")
            yield scrapy.Request(next_page, callback=self.parse_car_review, meta=response.meta)

    def parse_full_review(self, response):
        item = ScrapyDemoItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        full_review = soup.select('.quotation')
        full_review_text = full_review[0].get_text(strip=True) if full_review else ''
        item['brand_name'] = response.meta['brand_name']
        item['brand_url'] = response.meta['brand_url']
        item['car_name'] = response.meta['car_name']
        item['car_url'] = response.meta['car_url']
        item['full_review_url'] = response.meta['full_review_url']
        item['full_review'] = full_review_text
        yield item

# 主函数，用于启动爬虫
if __name__ == "__main__":
    # 检查当前模块是否作为主程序运行
    process = CrawlerProcess()
    # 创建一个CrawlerProcess实例，用于启动和管理爬虫
    process.crawl(ParkersCarSpider)
    # 将AutoCarSpider爬虫添加到进程中
    process.start()
    # 启动爬虫进程