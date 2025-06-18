from scrapy_demo.items import ScrapyDemoItem
from bs4 import BeautifulSoup
import requests
import time
import scrapy
import os
import csv  # 新增导入csv模块

class ParkersSpider(scrapy.Spider):
    name = "ParkersSpider"
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
                'overwrite': False,
                'header': False  # 添加这行，禁止自动写入表头
            }
        },
         'ITEM_PIPELINES': {
            'scrapy_demo.pipelines.DataCleaningPipeline': 200,
            'scrapy_demo.pipelines.CsvToJsonPipelineascii': 300
        }
    }
    def __init__(self, *args, **kwargs):
        super(ParkersSpider, self).__init__(*args, **kwargs)  # 修改类名大小写匹配
        # 初始化已存在的 full_review_url 集合
        self.existing_full_review_urls = set()
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        csv_file = os.path.join(output_dir, f'{self.name}-Output.csv')
        # 如果文件不存在，创建文件并写入表头
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', encoding='ascii', newline='',errors='replace') as f:
                writer = csv.DictWriter(f, fieldnames=['brand_name','brand_url','car_name','car_url','full_review_url','full_review'])
                writer.writeheader()
        # 如果文件存在，读取已有URL
        else:
            with open(csv_file, 'r', encoding='ascii', newline='',errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    full_review_url = row.get('full_review_url', '')
                    if full_review_url:
                        self.existing_full_review_urls.add(full_review_url)
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
                self.logger.info(f"该网页: {brand_url}下无车辆评价，跳过！")
                continue
            elif check_response.status_code == 400:
                self.logger.info(f"{brand_url}为无效链接！")
                continue
            yield scrapy.Request(brand_url, callback=self.parse_car, meta={'brand_name': brand_name, 'brand_url': brand_url})

    def parse_car(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        #在售车辆和旧车
        #car_links = soup.select('#latestModelsContainer h4 a, #olderModelsContainer h5 a')
        #在售车辆
        car_links = soup.select('#latestModelsContainer h4 a')
        for link in car_links:
            brand_name = response.meta['brand_name']
            brand_url = response.meta['brand_url']
            car_url = response.urljoin(link['href'])
            car_name = link.text.split('(')[0].strip()
            yield scrapy.Request(car_url, callback=self.parse_car_review, meta={'brand_name': brand_name, 'brand_url': brand_url, 'car_name': car_name, 'car_url': car_url})

    def parse_car_review(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = soup.select('li.owner-review-list__item article>a')
        for href in urls:
            full_review_text = ''
            review_elements = href.find_parent('article').select('div:nth-child(2) > div:nth-child(2) p')
            if review_elements:
                full_review_text = review_elements[0].get_text(strip=True)
            if full_review_text:
                full_review_url = response.urljoin(href['href'])
                if full_review_url not in self.existing_full_review_urls:
                    self.existing_full_review_urls.add(full_review_url)
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

if __name__ == '__main__':
    cmdline.execute("scrapy crawl ParkersSpider --nolog".split())
    