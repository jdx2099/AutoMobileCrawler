# AutoMobileCrawler

20250515

目前就两个爬虫功能，在终端中输入：

1，

scrapy crawl AutoCarList

爬取车质网所有车型的品牌、车系和车辆的名称及URL，车辆类型，投诉页面URL和车辆评分。

2，

scrapy crawl AutoCarSpider -a series_name="车辆名称"

爬取车质网内某一车辆的品牌、车辆及款式的名称，车辆页面URL，投诉页面URL及投诉内容。
