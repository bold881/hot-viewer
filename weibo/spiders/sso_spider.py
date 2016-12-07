import json
import scrapy
import base64

from weibo.items import WeiboItem
from scrapy.selector import Selector
from datetime import datetime


class SSOSpider(scrapy.Spider):
    name = 'weibo'
    start_urls = ['https://passport.weibo.cn/signin/login']

    def parse(self, response):
        return scrapy.FormRequest(
            url="https://passport.weibo.cn/sso/login",
            formdata={
                'username': '',
                'password': '',
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


    def parse_sso1(self, response):
        request = scrapy.http.Request(url="http://weibo.cn/pub/topmblog", callback=self.logged_in)
        request.meta['index'] = 1
        return request


    def logged_in(self, response):
        print response.url
        if 200 == response.status:
            contents = Selector(response).xpath('//div[@class="c" and @id]')
            for content in contents:
                item = WeiboItem()
                # weibo id
                item['id'] = content.xpath('@id').extract()
                # weibo user name
                item['nk'] = content.xpath('.//a[@class="nk"]/text()').extract()
                # weibo user href
                item['nkh'] = content.xpath('.//a[@class="nk"]/@href').extract()
                # is user verified
                item['isV'] = content.xpath('.//img[@alt="V"]/@src').extract()
                # is user weibo member
                item['isM'] = content.xpath('.//img[@alt="M"]/@src').extract()
                # weibo content
                item['ctt'] = content.xpath('.//span[@class="ctt"]/text()').extract()
                # first url of content image
                item['cttif'] = content.xpath('.//img[@class="ib"]/ancestor::*[1]/@href').extract()
                # content image
                item['ctti'] = content.xpath('.//img[@class="ib"]/@src').extract()
                # content image origin
                item['cttio'] = content.xpath('.//a[@class="cc"]/preceding-sibling::*[3]/@href').extract()
                # like count
                item['lc'] = content.xpath('.//a[@class="cc"]/preceding-sibling::*[2]/text()').extract()
                # like url
                item['lu'] = content.xpath('.//a[@class="cc"]/preceding-sibling::*[2]/@href').extract()
                # repost count
                item['rc'] = content.xpath('.//a[@class="cc"]/preceding-sibling::*[1]/text()').extract()
                # repost url
                item['ru'] = content.xpath('.//a[@class="cc"]/preceding-sibling::*[1]/@href').extract()
                # comment count
                item['ccc'] = content.xpath('.//a[@class="cc"]/text()').extract()
                # comment url 
                item['ccu'] = content.xpath('.//a[@class="cc"]/@href').extract()
                # collect url 
                item['cu'] = content.xpath('.//a[@class="cc"]/following-sibling::*[1]/@href').extract()
                # devide and time
                item['ct'] = content.xpath('.//span[@class="ct"]/text()').extract()
                # original html, base64 encoded
                item['rh'] = base64.b64encode((content.xpath('*').extract_first()).encode('utf-8'))
                # set crawlled time
                item['lt'] = str(datetime.now())
            
                yield item
        else:
            print "error: ", response.status
        index = response.meta['index']
        if index < 30:
            index += 1
        pageurl = "http://weibo.cn/pub/topmblog?page=%d" % index
        request = scrapy.http.Request(url=pageurl, callback=self.logged_in)
        request.meta['index'] = index
        yield request