import scrapy

class ScrapyDemoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    brand_name = scrapy.Field()
    brand_url = scrapy.Field()
    car_name = scrapy.Field()
    car_url = scrapy.Field()
    car_type = scrapy.Field()  # 新增的字段，用于存储车型类型
    type_url = scrapy.Field()  # 新增的字段，用于存储车型类型的URL
    score= scrapy.Field()  # 新增的字段，用于存储车型分数
    full_review_url= scrapy.Field()
    full_review = scrapy.Field()
    good_stuff = scrapy.Field()
    bad_stuff = scrapy.Field()
    verdict= scrapy.Field()
    model_name = scrapy.Field()  # 新增的字段，用于存储车型名称
    model_url = scrapy.Field()  # 新增的字段，用于存储车型URL
    model_type = scrapy.Field()  # 新增的字段，用于存储车型类型
    model_fuel_type = scrapy.Field()  # 新增的字段，用于存储车型燃料类型
    
class PakersSpiderItem(scrapy.Item):
    brand_name = scrapy.Field()
    brand_url = scrapy.Field()
    car_name = scrapy.Field()
    car_url = scrapy.Field()
    full_review_url = scrapy.Field()
    full_review = scrapy.Field()

class AutoCarListItem(scrapy.Item):
    brand_id = scrapy.Field()
    brand_name = scrapy.Field()
    brand_url = scrapy.Field()
    series_name = scrapy.Field()
    series_url = scrapy.Field()
    vehicle_id = scrapy.Field()
    car_name = scrapy.Field()
    car_url = scrapy.Field()
    vehicle_style = scrapy.Field()  # 新增的字段，用于存储车型类型
    car_type = scrapy.Field()  # 新增的字段，用于存储车型类型
    zlts_id = scrapy.Field()  # 新增的字段，用于存储投诉链接
    zlts_url = scrapy.Field()  # 新增的字段，用于存储投诉链接
    score= scrapy.Field()  # 新增的字段，用于存储车型分数
    full_review=scrapy.Field()  # 新增的字段，用于存储完整评论