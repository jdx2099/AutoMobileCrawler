import pymysql
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import validators
import json
import csv
import os
import chardet

class MysqlPipeline:
    def __init__(self):
        # 确保数据库连接参数正确
        self.connection = pymysql.connect(
            host='localhost',  # 添加host参数
            port=6023,      # 添加port参数
            user='root',
            password='root',
            db='scrapy_demo',
            charset='utf8mb4'  # 添加字符集
        )
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        table = """
        CREATE TABLE IF NOT EXISTS AutoCarList (
            id INT AUTO_INCREMENT PRIMARY KEY,
            brand_name VARCHAR(255) NOT NULL,
            brand_url VARCHAR(255) NOT NULL,
            series_name VARCHAR(255) NOT NULL,
            series_url VARCHAR(255) NOT NULL,
            car_name VARCHAR(255) NOT NULL,
            car_url VARCHAR(255) NOT NULL,
            car_type VARCHAR(255) NOT NULL,
            zlts_url VARCHAR(255) NOT NULL,
            score VARCHAR(255) NOT NULL,
            full_review TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        self.cursor.execute(table)
        self.connection.commit()

    def process_item(self, item, spider):
        try:
            self.cursor.execute("INSERT INTO douban(id,title, rating, quote) VALUES (%s,%s, %s, %s)",(0, item['title'], item['rating'], item['quote']))
            self.connection.commit()
        except pymysql.MySQLError as e:
            spider.logger.error(f"Error saving item: {e}")
            print(e)
        return item
        
    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

class DataCleaningPipeline:
    def process_item(self, item, spider):
        # 数据处理逻辑
        return item
        
class OptionValidationPipeline:
    def process_item(self, item, spider):
        # 添加验证逻辑
        if not item.get('brand_name'):
            raise scrapy.exceptions.DropItem("Missing brand_name")
        return item

class DataValidationPipeline:
    def process_item(self, item, spider):
        # 验证必要字段
        required_fields = ['brand_name', 'brand_url', 'car_name', 'car_url']
        for field in required_fields:
            if not item.get(field):
                raise DropItem(f"缺少必要字段: {field}")
        # 验证URL格式
        url_fields = ['brand_url', 'car_url']
        for field in url_fields:
            if not validators.url(item[field]):
                spider.logger.warning(f"无效的URL字段 {field}: {item[field]}")
                item[field] = None
        # 清理品牌名称
        item['brand_name'] = item['brand_name'].title()
        
        return item
        
class CsvToJsonPipelineutf8:
    def close_spider(self, spider):
        # 构造CSV和JSON文件路径，使用爬虫名称作为文件名前缀
        csv_path = os.path.join(spider.output_dir, f'{spider.name}-Output.csv')
        json_path = os.path.join(spider.output_dir, f'{spider.name}-Output.json')
        # 检查CSV文件是否存在且不为空
        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
            # 直接使用gbk编码打开CSV文件
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                # 获取spider中的car_name作为过滤关键词
                target_series = spider.car_name
                # 创建CSV字典阅读器
                reader = csv.DictReader(csv_file)
                # 将CSV数据转换为列表并根据car_name过滤
                if target_series:
                    data = [row for row in reader if row.get('car_name') == target_series]
                else:
                    data = list(reader)
                
                # 检查是否有实际数据
                if data:
                    # 将数据写入JSON文件，使用UTF-8编码
                    with open(json_path, 'w', encoding='utf-8') as json_file:
                        # 确保非ASCII字符不被转义，并添加缩进美化格式
                        json.dump(data, json_file, ensure_ascii=False, indent=2)
                else:
                    # 记录警告：CSV文件没有匹配的数据行
                    spider.logger.warning(f"CSV文件 {csv_path} 没有匹配{target_series}的数据行")
        else:
            # 记录警告：CSV文件不存在或为空
            spider.logger.warning(f"CSV文件 {csv_path} 不存在或为空")

class CsvToJsonPipelineascii:
    def close_spider(self, spider):
        # 构造CSV和JSON文件路径，使用爬虫名称作为文件名前缀
        csv_path = os.path.join(spider.output_dir, f'{spider.name}-Output.csv')
        json_path = os.path.join(spider.output_dir, f'{spider.name}-Output.json')
        # 检查CSV文件是否存在且不为空
        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
           # 直接使用gbk编码打开CSV文件
            with open(csv_path, 'r', encoding='ascii') as csv_file:
                # 创建CSV字典阅读器
                reader = csv.DictReader(csv_file)
                # 将CSV数据转换为列表
                data = list(reader)
                
                # 检查是否有实际数据
                if data:
                    # 将数据写入JSON文件，使用UTF-8编码
                    with open(json_path, 'w', encoding='ascii') as json_file:
                        # 确保非ASCII字符不被转义，并添加缩进美化格式
                        json.dump(data, json_file, ensure_ascii=False, indent=2)
                else:
                    # 记录警告：CSV文件没有有效数据行
                    spider.logger.warning(f"CSV文件 {csv_path} 没有有效数据行")
        else:
            # 记录警告：CSV文件不存在或为空
            spider.logger.warning(f"CSV文件 {csv_path} 不存在或为空")
    