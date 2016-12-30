# -*- coding: utf-8 -*-
import scrapy
import json
import time

from scrapy.selector import Selector
from weibo.items import UserItem
from weibo.items import FolloweeItem
from weibo.items import FanItem

class UserSpider(scrapy.Spider):
    name = 'weibouser'
    start_urls = ['https://passport.weibo.cn/signin/login']
    wurl = None

    def __init__(self, wurl=None, *args, **kwargs):
        super(UserSpider, self).__init__(*args, **kwargs)
        self.uhome = wurl
        self.mySqlPipeline = None

    def parse(self, response):
        return scrapy.FormRequest(
            url="https://passport.weibo.cn/sso/login",
            formdata={
                'username': 'xxx',
                'password': 'xxx',
                'savestate': '1',
                'ec': '0',
                'pagerefer': '',
                'entry': '',
                'wentry': '',
                'loginfrom': '',
                'client_id': '',
                'code': '',
                'qq': '',
                'hff': '',
                'hfp': ''},
            callback=self.login_click_parse,
            method='POST'
        )

    def login_click_parse(self, response):
        jsonresponse = json.loads(response.body)
        loginresulturl = "https:" + jsonresponse["data"]["loginresulturl"] + "&savestate=1&callback=jsonpcallback1480557882151"
        return scrapy.http.Request(url=loginresulturl, callback=self.parse_sso1)

    def parse_sso1(self, response): # go to specific weibo page
        #check arg wurl wether empty
        if self.uhome == None:
            self.uhome = self.mySqlPipeline.get_userurl()
            
        request = scrapy.http.Request(url=self.uhome, callback=self.parse_userhomepage)
        return request
    
    def parse_userhomepage(self, response):
        # from homepage to info
        usrinfo = response.selector.xpath(u'//a[text()="资料"]/@href').extract_first()
        usrinfo = "http://weibo.cn" + usrinfo
        request = scrapy.http.Request(url=usrinfo, callback=self.parse_repopage)
        return request

    def parse_repopage(self, response):
        if response.status == 200:
            item = UserItem()
            r1 = response.url.rfind('/')
            r2 = response.url[:r1].rfind('/')
            item['userid'] = response.url[r2+1:r1]
            item['photo'] = response.selector.xpath(u'//img[@alt="头像"]/@src').extract_first()
            item['ulevel'] = response.selector.xpath(u'//a[text()="送Ta会员"]/parent::*/text()').extract_first()

            medalArray = response.selector.xpath(u'//a[text()="送Ta会员"]/parent::*/img/@alt').extract()
            medal = ''
            for imedal in medalArray:
                medal += imedal + '|'
            item['medal'] = medal

            # get rest of info
            restArray = response.selector.xpath(u'//div[@class="tip" and text()="基本信息"]/following-sibling::*/text()').extract()
            for ri in restArray:
                if ri.find(u'昵称:') != -1:
                    item['nickname'] = ri[3:]
                    continue
                if ri.find(u'认证:') != -1:
                    item['certificate'] = ri
                    continue
                if ri.find(u'性别:') != -1:
                    item['sex'] = ri
                    continue
                if ri.find(u'地区:') != -1:
                    item['area'] = ri
                    continue
                if ri.find(u'生日:') != -1:
                    item['birthday'] = ri
                    continue
                if ri.find(u'认证信息：') != -1:
                    item['reginfo'] = ri
                    continue
                if ri.find(u'感情状况:') != -1:
                    item['marriagestate'] = ri
                    continue
                if ri.find(u'简介:') != -1:
                    item['briefintro'] = ri
                    continue
            if item['nickname'] == None:
                yield item
            
            tagArray = response.selector.xpath(u'//div[@class="c" and contains(., "标签:")]/a/text()').extract()
            ptag = ''
            for tai in tagArray:
                ptag += tai + '|'
            item['tag'] = ptag

            workArray = response.selector\
            .xpath(u'//div[@class="tip" and text()="工作经历"]/following-sibling::*[1]/text()').extract()
            pworkexp = ''
            for wei in workArray:
                pworkexp += wei + '|'
            item['workexp'] = pworkexp

            eduArray = response.selector\
            .xpath(u'//div[@class="tip" and text()="学习经历"]/following-sibling::*[1]/text()').extract()
            eduexp = ''
            for edi in eduArray:
                eduexp += edi + '|'
            item['education'] = eduexp

            extraInfo = response.selector\
            .xpath(u'//div[@class="tip" and text()="其他信息"]/following-sibling::*[1]/text()').extract()

            for exi in extraInfo:
                if exi.find(u'互联网:') != -1:
                    item['pc_home'] = exi
                    continue
                if exi.find(u'手机版:') != -1:
                    item['mobile_home'] = exi
                    continue
            yield item
            
            #get user following list
            urlfollow = response.url
            r1 = urlfollow.rfind('/')
            urlfollow = urlfollow[:r1+1] + 'follow'
            request = scrapy.http.Request(url=urlfollow, callback=self.parse_follow)
            request.meta['index'] = 1
            yield request

        else:
            print "!!!error status: " + response.status
    
    def parse_follow(self, response):
        if response.status == 200:
            r1 = response.url.rfind('/')
            r2 = response.url[:r1].rfind('/')
            curuserid = response.url[r2+1:r1]
            
            # get user in current page
            followees = Selector(response).xpath(u'//a[contains(., "关注他") or contains(., "关注她")]/parent::*/a[1]')
            for followee in followees:
                item = FolloweeItem()
                item['userid'] = curuserid
                item['followeeid'] = followee.xpath('.//text()').extract_first()
                item['followeeurl'] = followee.xpath('.//@href').extract_first()
                yield item

            # get total follow page
            maxpage = response.selector.xpath('//input[@name="mp" and @type="hidden"]/@value').extract_first()
            
            if maxpage != None: # only one page
                pageurl = "http://weibo.cn/%s/follow?page=2"%curuserid
                request = scrapy.http.Request(url=pageurl, callback=self.loopparse_followee)
                request.meta['maxpage'] = int(maxpage)
                request.meta['index'] = 2
                yield request


    def loopparse_followee(self, response):
        if response.status == 200:
            r1 = response.url.rfind('/')
            r2 = response.url[:r1].rfind('/')
            curuserid = response.url[r2+1:r1]
            
            # get user in current page
            followees = Selector(response).xpath(u'//a[contains(., "关注他") or contains(., "关注她")]/parent::*/a[1]')
            for followee in followees:
                item = FolloweeItem()
                item['userid'] = curuserid
                item['followeeid'] = followee.xpath('.//text()').extract_first()
                item['followeeurl'] = followee.xpath('.//@href').extract_first()
                yield item

            maxpage = response.meta['maxpage']
            index = response.meta['index']
            if index < maxpage:
                index += 1
                pageurl = "http://weibo.cn/%s/follow?page=%d"%(curuserid,index)
                request = scrapy.http.Request(url=pageurl, callback=self.loopparse_followee)
                request.meta['maxpage'] = maxpage
                request.meta['index'] = index
                yield request
            else:
                # run get fans request
                urlfans = response.url
                r1 = urlfans.rfind('/')
                urlfans = urlfans[:r1+1] + 'fans'
                request = scrapy.http.Request(url=urlfans, callback=self.parse_fans)
                request.meta['index'] = 1
                yield request


    def parse_fans(self, response):
        if response.status == 200:
            r1 = response.url.rfind('/')
            r2 = response.url[:r1].rfind('/')
            curuserid = response.url[r2+1:r1]
            
            # get user in current page
            fans = Selector(response).xpath(u'//a[contains(., "关注他") or contains(., "关注她")]/parent::*/a[1]')
            for fan in fans:
                item = FanItem()
                item['userid'] = curuserid
                item['fansid'] = fan.xpath('.//text()').extract_first()
                item['fansurl'] = fan.xpath('.//@href').extract_first()
                yield item

            # get total fans page
            maxpage = response.selector.xpath('//input[@name="mp" and @type="hidden"]/@value').extract_first()
            
            if maxpage != None: # only one page
                pageurl = "http://weibo.cn/%s/fans?page=2"%curuserid
                request = scrapy.http.Request(url=pageurl, callback=self.loopparse_fans)
                request.meta['maxpage'] = int(maxpage)
                request.meta['index'] = 2
                yield request


    def loopparse_fans(self, response):
        if response.status == 200:
            r1 = response.url.rfind('/')
            r2 = response.url[:r1].rfind('/')
            curuserid = response.url[r2+1:r1]
            
            # get user in current page
            fans = Selector(response).xpath(u'//a[contains(., "关注他") or contains(., "关注她")]/parent::*/a[1]')
            for fan in fans:
                item = FanItem()
                item['userid'] = curuserid
                item['fansid'] = fan.xpath('.//text()').extract_first()
                item['fansurl'] = fan.xpath('.//@href').extract_first()
                yield item

            maxpage = response.meta['maxpage']
            index = response.meta['index']
            if index < maxpage:
                index += 1
                pageurl = "http://weibo.cn/%s/fans?page=%d"%(curuserid,index)
                request = scrapy.http.Request(url=pageurl, callback=self.loopparse_fans)
                request.meta['maxpage'] = maxpage
                request.meta['index'] = index
                yield request
            else:
                homeurl = self.mySqlPipeline.get_userurl()
                request = scrapy.http.Request(url=homeurl, callback=self.parse_userhomepage)
                yield request