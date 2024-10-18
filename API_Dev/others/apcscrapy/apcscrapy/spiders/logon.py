import scrapy
from scrapy import Request, signals
from scrapy.http import FormRequest
from pydispatch import dispatcher

class APCSpider(scrapy.Spider):
    name = 'APC_spider'
    start_urls = ['http://10.96.184.44/Forms/login1']
    base_url = None
    
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
    
    def parse(self, response):
        return FormRequest.from_response(
            response,
            formdata={
                'login_username': 'readonly',
                'login_password': '123456',
                'submit': 'Log On'
            },
            callback=self.after_login
        )

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
        load_data = response.xpath("//table[@class='data']//table/tr[2]/td[2]/span/text()").extract_first()
        peak_load_data = response.xpath("//table[@class='data']//table/tr[3]/td[2]/span/text()").extract_first()
        energy_data = response.xpath("//table[@class='data']//table/tr[4]/td[2]/span/text()").extract_first()
        
        status['load_data'] = load_data
        status['peak_load_data'] = peak_load_data
        status['energy_data'] = energy_data
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