# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()             # weibo id like 'M_EknySBjCV'
    nk = scrapy.Field()             # weibo user name
    nkh = scrapy.Field()            # user href
    isV = scrapy.Field()            # user is verified
    isM = scrapy.Field()            # user is Member
    ctt = scrapy.Field()            # weibo text content
    #cttimgall = scrapy.Field()     # (optional) all weibo content image url
    cttif = scrapy.Field()          # (optional) weibo content image url(maybe first if there more)
    ctti = scrapy.Field()           # weibo content img url
    cttio = scrapy.Field()          # weibo content img original
    lc = scrapy.Field()             # like count
    lu = scrapy.Field()             # like url
    rc = scrapy.Field()             # repost count
    ru = scrapy.Field()             # repost url
    ccc = scrapy.Field()            # comment cccount
    ccu = scrapy.Field()            # comment url
    cu = scrapy.Field()             # weibo collect
    ct = scrapy.Field()             # device & time
    rh = scrapy.Field()             # original html data
    lt = scrapy.Field()             # time got by spider
    
class UserItem(scrapy.Item):
    userid = scrapy.Field()
    photo = scrapy.Field()
    ulevel = scrapy.Field()
    medal = scrapy.Field()
    nickname = scrapy.Field()
    certificate = scrapy.Field()
    sex = scrapy.Field()
    area = scrapy.Field()
    birthday = scrapy.Field()
    reginfo = scrapy.Field()
    marriagestate = scrapy.Field()
    briefintro = scrapy.Field()
    tag = scrapy.Field()
    workexp = scrapy.Field()
    education = scrapy.Field()
    pc_home = scrapy.Field()
    mobile_home = scrapy.Field()
