# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from urllib.parse import urlencode
import requests
from random import random , randint
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class BookscraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BookscraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)



class ScrapeOpsFakeUAMiddleware:
    
    @classmethod
    def from_crawler(cls,crawler):
        """
        This is a class method used as an alternate constructor.
        Purpose:
        ------------
        Scrapy provides a `crawler` object which holds project-wide settings.
        This method extracts the settings from the crawler and creates
        an instance of ScrapeOpsFakeUA with those settings.

        Parameters:
        ------------
        crawler : Crawler object from Scrapy
            Contains access to global settings, spiders, middlewares, etc.

        Returns:
        ------------
        An instance of ScrapeOpsFakeUA initialized with the crawler's settings.
        """

        return cls(crawler.settings)

    def __init__(self,settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint= settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT','https://headers.scrapeops.io/v1/user-agents')
        self.scrapeops_fake_user_agents_active = settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENABLED',False)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []
        self._get_user_agents_list()
        self._scrapeops_fake_user_agents_enabled()


    def _get_user_agents_list(self):
        payload = {'api_key':self.scrapeops_api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        
        # Make a GET request to the ScrapeOps endpoint with the payload as query parameters
        # NOTE: urlencode converts the dictionary into a URL-encoded string like "api_key=XYZ&num_results=5"
        response = requests.get(self.scrapeops_endpoint,params=urlencode(payload))

        # Parse the JSON response body into a Python dictionary
        json_response = response.json()

        self.user_agents_list = json_response.get('result', [])

    def _get_random_user_agent(self):
        random_index = randint(0, len(self.user_agents_list)-1)
        return self.user_agents_list[random_index]
    
    
    def _scrapeops_fake_user_agents_enabled(self):
        if self.scrapeops_api_key is None or self.scrapeops_api_key =='' or not self.user_agents_list:
            self.scrapeops_fake_user_agents_active = False
        else:
            self.scrapeops_fake_user_agents_active = True

    def process_request(self,request,spider):
        random_user_agent = self._get_random_user_agent()
        request.headers['User-Agent'] = random_user_agent

        print("********************************")
        print(request.headers['User-Agent'])



class ScrapeOpsFakeHeaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_BROWSER_HEADER_ENDPOINT', 'https://headers.scrapeops.io/v1/browser-headers')
        self.scrapeops_fake_browser_headers_active = settings.get('SCRAPEOPS_FAKE_BROWSER_HEADER_ENABLED', False)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []
        self._get_headers_list()
        self._scrapeops_fake_browser_headers_enabled()

    def _get_headers_list(self):
        payload = {'api_key': self.scrapeops_api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        try:
            response = requests.get(self.scrapeops_endpoint, params=payload)
            json_response = response.json()
            self.headers_list = json_response.get('result', [])
        except Exception as e:
            print(f"[ScrapeOpsFakeHeaderMiddleware] Error fetching headers: {e}")
            self.headers_list = []

    def _get_random_browser_header(self):
        if not self.headers_list:
            return None
        return self.headers_list[randint(0, len(self.headers_list) - 1)]

    def _scrapeops_fake_browser_headers_enabled(self):
        self.scrapeops_fake_browser_headers_active = bool(self.scrapeops_api_key and self.headers_list)

    def process_request(self, request, spider):
        if not self.scrapeops_fake_browser_headers_active:
            return

        random_browser_header = self._get_random_browser_header()
        if not random_browser_header:
            return

        # Safely assign headers from random_browser_header
        for header_key, header_value in random_browser_header.items():
            if header_key and header_value:
                request.headers[header_key] = header_value

        spider.logger.debug(f"[ScrapeOpsFakeHeaderMiddleware] Injected headers: {random_browser_header}")

            
