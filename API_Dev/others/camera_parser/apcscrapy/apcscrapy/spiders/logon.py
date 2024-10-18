import os
import json
import scrapy
from scrapy import Request, signals
from scrapy.http import FormRequest
from pydispatch import dispatcher

class APCSpider(scrapy.Spider):
    name = 'APC_spider'
    # start_urls = ['http://10.96.177.133/resource/measurements']
    base_url = None
    custom_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6,ja;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'PHPSESSID=deb482672413a6515473ec1a059b2cfc; distanceUnit=metric; temperatureUnit=celsius',
        'Host': '10.96.177.133',
        'Pragma': 'no-cache',
        'Referer': 'http://10.96.177.133/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    cookies = {
        'PHPSESSID': 'deb482672413a6515473ec1a059b2cfc',
        'distanceUnit': 'metric',
        'temperatureUnit': 'celsius',
    }
    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        
    @property
    def logoff_url(self):
        return f"{self.base_url}/logout.htm"
    
    @property
    def loadman_url(self):
        return f"{self.base_url}/loadman.htm"
    
    @property
    def phload_url(self):
        return f"{self.base_url}/phload.htm"
    
    @property
    def bankload_url(self):
        return f"{self.base_url}/bankload.htm"

    def start_requests(self):
        # print("parse:"+self.start_urls[0])
        yield Request(
            url='http://10.96.177.133/resource/measurements',
            cookies=self.cookies,
            meta={'dont_redirect': True},
            dont_filter=True,
            callback=self.test_res
        )

    def test_res(self, res):
        print("test_res:"+res)

    def after_login(self, response):
        try:
            self.base_url = response.url.split('/home.htm')[0]
            yield Request(url=self.loadman_url,
                                  callback=self.parse_loadman_page)
            yield Request(url=self.phload_url,
                                    callback=self.parse_phload_page)
            yield Request(url=self.bankload_url,
                                    callback=self.parse_bankload_page)      
        except:
            self.logger.error("failed to login")
        
    def parse_loadman_page(self, response):
        status = dict()
        load_data = response.xpath("/html/body/div[1]/div[2]/div[2]/div[3]/div/div[1]/div[2]/div[2]/p/text()").extract_first()
        # peak_load_data = response.xpath("//table[@class='data']//table/tr[3]/td[2]/span/text()").extract_first()
        # energy_data = response.xpath("//table[@class='data']//table/tr[4]/td[2]/span/text()").extract_first()
        
        status['load_data'] = load_data
        # status['peak_load_data'] = peak_load_data
        # status['energy_data'] = energy_data
        yield status
        yield Request(url=self.logoff_url, callback=self.after_logoff)
    
    def parse_phload_page(self, response):
        pass

    def parse_bankload_page(self, response):
        pass
    
    def after_logoff(self, response):
        self.logger.info("logoff success")
        
    def spider_closed(self, spider):
        yield Request(url=self.logoff_url, callback=self.after_logoff)


if __name__ == '__main__':
    import requests

    # URL to request
    url = 'http://10.96.177.133/resource/measurements'

    # Define headers
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6,ja;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'PHPSESSID=deb482672413a6515473ec1a059b2cfc; distanceUnit=metric; temperatureUnit=celsius',
        'Host': '10.96.177.133',
        'Pragma': 'no-cache',
        'Referer': 'http://10.96.177.133/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # Send GET request
    response = requests.get(url, headers=headers)

    # Print the response content
    print(f"Response URL: {response.url}")
    # print(f"Response Content: {response.text}")
    # data = response.text
    print(response.text)
