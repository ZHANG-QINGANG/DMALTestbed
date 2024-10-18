import time
import numpy as np
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request, FormRequest
from scrapy import signals
from pydispatch import dispatcher
import json
import scrapy


class APCSpider(scrapy.Spider):
    name = 'APC_spider'
    start_urls = ['http://10.96.184.44/Forms/login1']
    scraped_data = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    @property
    def logoff_url(self):
        return f"{self.base_url}/logout.htm"

    @property
    def loadman_url(self):
        return f"{self.base_url}/loadman.htm"

    # Simulate login
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

    # After successful login, visit multiple pages to scrape data
    def after_login(self, response):
        try:
            self.base_url = response.url.split('/home.htm')[0]
            yield Request(url=self.loadman_url, callback=self.parse_loadman_page)
        except Exception as e:
            self.logger.error(f"Login failed: {e}")

    def parse_loadman_page(self, response):
        load_data = response.xpath("//table[@class='data']//table/tr[2]/td[2]/span/text()").extract_first()
        if not load_data:
            self.logger.warning("Failed to extract load data")
        else:
            self.logger.info(f"Extracted load data: {load_data}")
            print(json.dumps(load_data.split()[0]))
            APCSpider.scraped_data.append({'load_data': load_data})

        # After scraping, log out
        yield Request(url=self.logoff_url, callback=self.after_logoff)

    # Callback after successful logoff
    def after_logoff(self, response):
        self.logger.info("Logoff success")

    def spider_closed(self, spider):
        self.logger.info("Spider closed, performing logoff.")
        yield Request(url=self.logoff_url, callback=self.after_logoff)


# Run the crawler and return the data
def run_crawler():
    process = CrawlerProcess(settings={
        "LOG_ENABLED": True,  # Enable logging
    })

    # 直接传递爬虫类
    process.crawl(APCSpider)
    process.start()  # Block until the crawler is finished

    # Return the scraped data from the class variable
    return APCSpider.scraped_data


if __name__ == '__main__':
    try:
        results = run_crawler()
        # if results:
        #     load_data_kw = results[0]["load_data"].split()[0]
        #     load_data_w = np.array(load_data_kw).astype(np.float64) * 1000
        #     print(load_data_w)
        # else:
        #     print("No data was scraped.")
    except Exception as e:
        print(f"Error running the crawler: {e}")
