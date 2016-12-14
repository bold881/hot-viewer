from __future__ import absolute_import, unicode_literals
from . celery import app
from .spiders.sso_spider import do_crawl

@app.task
def docrawl(x, y):
    do_crawl()