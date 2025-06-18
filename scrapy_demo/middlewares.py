# 移除不存在的导入
from fake_useragent import UserAgent  # 确保已安装fake-useragent
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

# middlewares.py
class RandomUserAgentMiddleware:
    def process_request(self, request, spider):
        request.headers["User-Agent"] = UserAgent().random
        #request.headers["Referer"] = "https://www.12365auto.com/"

class PurposeHeaderMiddleware:
    def process_request(self, request, spider):
        request.headers["X-Purpose"] = "Academic Research: Vehicle Quality Analysis"  # 可扩展为随机选择声明

class OneMiddleware(object):
    def process_request(self, request, spider):
        print('one 请求')

    def process_response(self, request, response, spider):
        print('one 响应')
        # return None

class TwoMiddleware(object):
    def process_request(self, request, spider):
        print('two 请求')

    def process_response(self, request, response, spider):
        print('two 响应')
        return response


from twisted.internet.error import ConnectionLost

class CustomRetryMiddleware:
    def process_exception(self, request, exception, spider):
        if isinstance(exception, ConnectionLost):
            return request.copy(dont_filter=True)

class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if response.status in [403, 429]:
            reason = f'触发反爬机制(HTTP {response.status})'
            return self._retry(request, reason, spider) or response
        return super().process_response(request, response, spider)

