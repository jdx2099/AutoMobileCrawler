import pymysql
from itemadapter import ItemAdapter

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


from scrapy.exceptions import DropItem
import validators

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
    