from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from apcscrapy.spiders.logon import APCSpider

from fastapi import FastAPI, BackgroundTasks
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import requests
from flask import Flask, request, jsonify

import json, os
import uvicorn

app = FastAPI()


def run_crawler():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "items.jsonl": {"format": "jsonl"},
        }
    })
    process.crawl(APCSpider)
    process.start()

def run_crawler_cmd():
    cmd = "scrapy crawl APC_spider -o items.jsonl"
    os.system(cmd)

@app.get("/get_data")
def trigger_crawler():
    # read jsonl
    with open('items.jsonl', 'r') as f:
        data = f.readlines()
        init_length = len(data)
    print("start")
    
    # run scrapy in terminal
    run_crawler_cmd()
    
    # check if the file is updated
    while True:
        with open('items.jsonl', 'r') as f:
            data = f.readlines()
            if len(data) > init_length:
                break
    # return the last line
    return json.loads(data[-1])

@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get()
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=1115)

def run_everything():
    uvicorn.run(app, host="0.0.0.0", port=1115)
