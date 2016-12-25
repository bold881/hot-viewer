import scrapy
import json

from scrapy.selector import Selector

class RepoSpider(scrapy.Spider):
    name = 'repoweibo'
    start_urls = ['https://passport.weibo.cn/signin/login']
    wurl = None

    def __init__(self, wurl=None, *args, **kwargs):
        super(RepoSpider, self).__init__(*args, **kwargs)
        self.wurl = wurl

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
        request = scrapy.http.Request(url=self.wurl, callback=self.parse_repopage)
        return request

    def parse_repopage(self, response):
        if response.status == 200:
            print response.selector.xpath('//div[@class="c"]/a[@href]/text()').extract()
            maxpage = response.selector.xpath('//input[@name="mp" and @type="hidden"]/@value').extract_first()
            
            if maxpage != None: # only one page
                request = scrapy.http.Request(url='%s2'%self.wurl, callback=self.parse_following_page)
                request.meta['maxpage'] = int(maxpage)
                request.meta['index'] = 2
                return request
        else:
            print "!!!error status: " + response.status 

    def parse_following_page(self, response):
        print response.selector.xpath('//div[@class="c"]/a[@href]/text()').extract()
        index = response.meta['index']
        maxpage = response.meta['maxpage']
        if index < maxpage:
            index += 1
            request = scrapy.http.Request(url='%s%d'%(self.wurl, index), callback=self.parse_following_page)
            request.meta['maxpage'] = maxpage
            request.meta['index'] = index
            return request

        