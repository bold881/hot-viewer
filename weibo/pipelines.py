# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log


#class WeiboPipeline(object):
 #   def process_item(self, item, spider):
  #      return item

class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
    
    def process_item(self, item, spider):
        query = self.collection.find({"id":item['id']})
        if query.count() > 0:
            raise DropItem("Exist item: ", item['id'])
        else:
            self.collection.insert(dict(item))
    
        return item