# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy.selector import Selector
from weibo.items import UserItem

class RepoSpider(scrapy.Spider):
    name = 'weibouser'
    start_urls = ['https://passport.weibo.cn/signin/login']
    wurl = None

    def __init__(self, wurl=None, *args, **kwargs):
        super(RepoSpider, self).__init__(*args, **kwargs)
        self.uinfo = wurl

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
        request = scrapy.http.Request(url=self.uinfo, callback=self.parse_repopage)
        return request

    def parse_repopage(self, response):
        if response.status == 200:
            item = UserItem()
            r1 = self.uinfo.rfind('/')
            r2 = self.uinfo[:r1].rfind('/')
            item['userid'] = self.uinfo[r2+1:r1]
            item['photo'] = response.selector.xpath(u'//img[@alt="头像"]/@src').extract()
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
                    item['nickname'] = ri
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
                if ri.find(u'认证信息:') != -1:
                    item['reginfo'] = ri
                    continue
                if ri.find(u'感情状况:') != -1:
                    item['marriagestate'] = ri
                    continue
                if ri.find(u'简介:') != -1:
                    item['briefintro'] = ri
                    continue
            
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
        else:
            print "!!!error status: " + response.status