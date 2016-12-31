# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import MySQLdb

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from weibo.items import UserItem
from weibo.items import FolloweeItem
from weibo.items import FanItem
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

class MysqlDBPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(
            settings['MYSQL_HOST'],
            settings['MYSQL_USER'],
            settings['MYSQL_PSWD'],
            settings['MYSQL_DBNAME'],
            charset=settings['MYSQL_CHARSET'],
            use_unicode=settings['MYSQL_UNICODE']
        )
        self.cursor = self.conn.cursor()
    add_user = ("INSERT INTO user "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "
                "%s, %s, %s, %s, %s, %s, %s, %s)")
    
    add_followee = ("INSERT INTO follow"
                    "VALUES ('%s', '%s', '%s')")
    
    def get_userurl(self):
        try:
            self.cursor.execute("select followeeurl from follow where (followeeid not in (select nickname from user)) and (followeeurl not in (select mobile_home from user)) limit 1")
            return self.cursor.fetchone()[0]
        except MySQLdb.Error, e:
            print "DB Error %d: %s" % (e.args[0], e.args[1])
    def open_spider(self, spider):
        spider.mySqlPipeline = self
    
    def process_item(self, item, spider):

        if spider.name == 'weibouser' and \
        isinstance(item, UserItem):
            if item['nickname'] == None:
                raise DropItem(item)
            try:
                #check if item exist
                self.cursor.execute("SELECT COUNT(*) FROM user where userid = '%s'"%item['userid'])
                if int(self.cursor.fetchone()[0]) > 0:
                    #print "%s exist!!!"%item['userid']
                   return item
                
                #insert new data
                data_user = (item['userid'], item.get('photo', ''), item.get('ulevel', ''), item.get('medal', ''), \
                item.get('nickname', ''), item.get('certificate', ''), item.get('sex', ''), item.get('area', ''), \
                item.get('birthday', ''), item.get('reginfo', ''), item.get('marriagestate', ''), \
                item.get('briefintro', ''), item.get('tag', ''), item.get('workexp', ''), \
                item.get('education', ''), item.get('pc_home', ''), item.get('mobile_home', ''))

                self.cursor.execute(self.add_user, data_user)
                #self.cursor.execute(errorsql)
                self.conn.commit()
            except MySQLdb.Error, e:
                print "DB Error %d: %s" % (e.args[0], e.args[1])
        
        elif spider.name == 'weibouser' and \
        isinstance(item, FolloweeItem):
            try:
                self.cursor.execute("SELECT COUNT(*) FROM follow where userid = '%s' and followeeid='%s'"%(item['userid'],item['followeeid']))
                if int(self.cursor.fetchone()[0]) > 0:
                    return item
                #data_followee = (item.get('userid', ''), item.get('followeeid', ''), item.get('followeeurl', ''))
                #self.cursor.execute(self.add_followee, data_followee)
                insertsql = "INSERT INTO follow VALUES('%s', '%s', '%s')"%(item.get('userid', ''), item.get('followeeid', ''), item.get('followeeurl', ''))
                #print insertsql
                self.cursor.execute(insertsql)
                self.conn.commit()
            except MySQLdb.Error, e:
                print "DB Error %d: %s" % (e.args[0], e.args[1])

        elif spider.name == 'weibouser' and \
        isinstance(item, FanItem):
            try:
                self.cursor.execute("SELECT COUNT(*) FROM fans where userid = '%s' and fansid='%s'"%(item['userid'],item['fansid']))
                if int(self.cursor.fetchone()[0]) > 0:
                    return item
                
                insertsql = "INSERT INTO fans VALUES('%s', '%s', '%s')"%(item.get('userid', ''), \
                item.get('fansid', ''), item.get('fansurl', ''))
                
                self.cursor.execute(insertsql)
                self.conn.commit()
            except MySQLdb.Error, e:
                print "DB Error %d: %s" % (e.args[0], e.args[1])

        return item