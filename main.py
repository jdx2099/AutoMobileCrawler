from fastapi import FastAPI, Body, HTTPException, status, Request, Response
# 导入FastAPI框架的核心组件，用于构建API服务
from scrapy.crawler import CrawlerRunner
# 导入Scrapy的CrawlerRunner，用于运行爬虫
from scrapy.utils.project import get_project_settings
# 导入获取Scrapy项目配置的方法
from twisted.internet import reactor
# 导入Twisted框架的reactor，用于异步事件处理
from pydantic import BaseModel
# 导入Pydantic的BaseModel，用于数据验证和设置
from fastapi.responses import JSONResponse
# 导入FastAPI的JSON响应类
import os
# 导入操作系统相关功能
import asyncio
# 导入Python异步IO库
import traceback
# 导入异常堆栈跟踪模块
import json
# 导入JSON处理模块
import time
# 导入时间处理模块
from threading import Thread
# 导入Python标准库中的Thread类，用于创建和管理线程
from queue import Queue
# 导入Python标准库中的Queue类，用于线程间安全的数据交换
from datetime import datetime
# 导入Python标准库中的datetime类，用于处理日期和时间
app = FastAPI()

os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapy_demo.settings'

class CrawlResponse(BaseModel):
    status: str
    data: list = []
    item_count: int = 0
    error: str = None
    execution_time: float = None

class SpiderRequest(BaseModel):
    car_name: str
@app.post("/autocar_spider")
async def autocar_spider(request: SpiderRequest = Body(...)):
    # 1. 打印分隔线标记请求开始
    print("=============================")
    # 2. 从请求体中获取车型系列名称
    car_name = request.car_name
    # 3. 记录开始时间用于计算执行时长
    start_time = time.time()
    
    try:
        # 4. 使用线程+队列方式运行Scrapy爬虫
        # 5. 创建结果队列用于线程间通信
        result_queue = Queue()
        # 6. 定义爬虫运行函数
        def run_spider():
            try:
                # 7. 获取Scrapy项目配置
                settings = get_project_settings()
                # 8. 创建爬虫运行器
                runner = CrawlerRunner(settings)
                # 9. 初始化数据收集列表
                crawl_data = []
                # 10. 定义数据收集回调函数
                def collect_data(item):
                    crawl_data.append(dict(item))
                
                # 11. 启动爬虫并设置回调
                deferred = runner.crawl(
                    'AutoCarSpider',  # 爬虫名称
                    car_name=car_name  # 传递参数
                )
                # 12. 爬虫完成后将数据放入队列
                deferred.addCallback(lambda _: result_queue.put(crawl_data))
                # 13. 启动Twisted事件循环
                reactor.run(installSignalHandlers=0)
                
                # 14. 异常处理：将错误信息放入队列
            except Exception as e:
                result_queue.put({
                    'error': str(e),
                    'end_time': time.time()
                })
        # 15. 创建并启动爬虫线程
        thread = Thread(target=run_spider)
        #thread.daemon = True  # 设置为守护线程
        thread.start()
        # 16. 设置60秒超时等待
        thread.join(60)
        # 17. 检查队列是否为空（超时或异常）
        if result_queue.empty():
            return JSONResponse(
                status_code=500,
                content={"status": "error", "error": "Timeout or no data received"}
                
            )
        # 18. 返回成功响应（当前版本注释了数据处理逻辑）
        return JSONResponse(
            status_code=200,
            content={
                "status": "processing",
                "message": "车质网车型爬虫任务已开始执行",
                "task_id": str(hash(car_name))[:8],  # 生成简单任务ID
                "Start_time":f"{datetime.fromtimestamp(start_time).strftime('%H:%M:%S')}"
            }
        )

    except Exception as e:
        # 19. 全局异常处理
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "stack_trace": traceback.format_exc()
            }
        )

@app.post("/autocarlist_spider")
async def autocarlist_spider():
    print("=============================")
    start_time = time.time()
    
    try:
        result_queue = Queue()
        
        def run_spider():
            try:
                settings = get_project_settings()
                settings.set('LOG_ENABLED', True)  # 确保日志启用
                settings.set('LOG_LEVEL', 'INFO')  # 设置日志级别
                runner = CrawlerRunner(settings)
                crawl_data = []
                
                deferred = runner.crawl('AutoCarList')
                deferred.addCallback(lambda _: result_queue.put({
                    'status': 'completed',
                    'data': crawl_data,
                    'execution_time': time.time() - start_time
                }))
                deferred.addCallback(lambda _: reactor.stop())
                reactor.run(installSignalHandlers=0)
                
            except Exception as e:
                result_queue.put({
                    'error': str(e),
                    'stack_trace': traceback.format_exc()
                })

        thread = Thread(target=run_spider)
        thread.daemon = True  # 设置为守护线程
        thread.start()
        #thread.join()
        return JSONResponse(
            status_code=200,
            content={
                "status": "processing",
                "message": "车质网车型列表爬虫任务已开始执行",
                #"task_id": str(hash(str(time.time())))[:8],
                "Start_time":f"{datetime.fromtimestamp(start_time).strftime('%H:%M:%S')}"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "stack_trace": traceback.format_exc()
            }
        )


@app.post("/parkerscar_spider")
async def parkerscar_spider(request: SpiderRequest = Body(...)):
    # 1. 打印分隔线标记请求开始
    print("=============================>>>")
    # 2. 从请求体中获取车型系列名称
    car_name = request.car_name
    # 3. 记录开始时间用于计算执行时长
    start_time = time.time()
    
    try:
        # 4. 使用线程+队列方式运行Scrapy爬虫
        # 5. 创建结果队列用于线程间通信
        result_queue = Queue()
        # 6. 定义爬虫运行函数
        def run_spider():
            try:
                # 7. 获取Scrapy项目配置
                settings = get_project_settings()
                # 8. 创建爬虫运行器
                runner = CrawlerRunner(settings)
                # 9. 初始化数据收集列表
                crawl_data = []
                # 10. 定义数据收集回调函数
                def collect_data(item):
                    print(f"Collected item: {item}")  # 添加收集日志
                    crawl_data.append(dict(item))
                
                # 11. 启动爬虫并设置回调
                deferred = runner.crawl('ParkersCarSpider', car_name=car_name)
                deferred.addCallback(lambda _: result_queue.put({
                    'data': crawl_data,
                    'output_files': os.listdir(settings.get('OUTPUT_DIR'))  # 检查输出文件
                }))
                reactor.run(installSignalHandlers=0)
                
                # 14. 异常处理：将错误信息放入队列
            except Exception as e:
                result_queue.put({
                    'error': str(e),
                    'end_time': time.time()
                })
        # 15. 创建并启动爬虫线程
        thread = Thread(target=run_spider)
        #thread.daemon = True  # 设置为守护线程
        thread.start()
        # 16. 设置420秒超时等待
        thread.join(420)
        # 17. 检查队列是否为空（超时或异常）
        if result_queue.empty():
            return JSONResponse(
                status_code=500,
                content={"status": "error", "error": "Timeout or no data received"}
                
            )
        # 18. 返回成功响应（当前版本注释了数据处理逻辑）
        return JSONResponse(
            status_code=200,
            content={
                "status": "processing",
                "message": "Parkers车辆评论爬虫任务已开始执行",
                "task_id": str(hash(car_name))[:8],  # 生成简单任务ID
                "Start_time":f"{datetime.fromtimestamp(start_time).strftime('%H:%M:%S')}"
            }
        )

    except Exception as e:
        # 19. 全局异常处理
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "stack_trace": traceback.format_exc()
            }
        )

@app.post("/parkers_spider")
async def parkers_spider():
    print("=============================")
    start_time = time.time()
    
    try:
        result_queue = Queue()
        
        def run_spider():
            try:
                settings = get_project_settings()
                settings.set('LOG_ENABLED', True)  # 确保日志启用
                settings.set('LOG_LEVEL', 'INFO')  # 设置日志级别
                runner = CrawlerRunner(settings)
                crawl_data = []
                
                deferred = runner.crawl('ParkersSpider')
                deferred.addCallback(lambda _: result_queue.put({
                    'status': 'completed',
                    'data': crawl_data,
                    'execution_time': time.time() - start_time
                }))
                deferred.addCallback(lambda _: reactor.stop())
                reactor.run(installSignalHandlers=0)
                
            except Exception as e:
                result_queue.put({
                    'error': str(e),
                    'stack_trace': traceback.format_exc()
                })

        thread = Thread(target=run_spider)
        thread.daemon = True  # 设置为守护线程
        thread.start()
        #thread.join()
        return JSONResponse(
            status_code=200,
            content={
                "status": "processing",
                "message": "车质网车型列表爬虫任务已开始执行",
                #"task_id": str(hash(str(time.time())))[:8],
                "Start_time":f"{datetime.fromtimestamp(start_time).strftime('%H:%M:%S')}"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "stack_trace": traceback.format_exc()
            }
        )

@app.get("/")
async def root():
    return {"message": "API服务运行中"}

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse
    return FileResponse("favicon.ico")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
#uvicorn main:app --reload


