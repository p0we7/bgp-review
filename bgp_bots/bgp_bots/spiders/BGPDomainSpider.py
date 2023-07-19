# -*- coding: utf-8 -*-
import scrapy
from bgp_bots.spiders import BaseSpider
from bgp_bots.items import DomainItem
from scrapy.utils.response import open_in_browser
from scrapy_splash import SplashRequest, SlotPolicy

from warehouse.models import ASN


class BgpdomainspiderSpider(BaseSpider):
    name = 'BGPDomainSpider'
    allowed_domains = ['bgp.he.net']
    start_urls = ['https://bgp.he.net/AS4134']

    custom_settings = {
        'ITEM_PIPELINES': {
            'bgp_bots.pipelines.DjangoDomainPipeline': 302,
        }
    }

    retry_xpath = '//*[@id="error"]/text()'

    cookies = {}

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        # spider.start_urls = self.generator_prefix_url_from_db(crawler)
        # Question : why invoking self class need `crawler` argument ?
        return spider


    def start_requests(self):

        yield SplashRequest(url=self.start_urls[0],
                            callback=self.parse,
                            endpoint='execute',
                            args={
                                'lua_source': self.lua_script,
                                'download_timeout': 60
                            },
                            slot_policy=SlotPolicy.SCRAPY_DEFAULT
                        )




    def parse(self, response):

        self.cookies = self.format_cookies_for_request(response)

        prefix_url = self.generator_prefix_url_from_db()

        # for url in prefix_url[:5]: # this is for development
        # for url in [ 'https://bgp.he.net/net/202.168.153.0/24' ]:
        for url in prefix_url:
            yield SplashRequest(url, callback=self.parse_domain,
                                    dont_filter=True,
                                    cookies=self.cookies)


    def generator_prefix_url_from_db(self):
        request_urls = []

        for asn in ASN.objects.filter(crawled=False):
            if not asn.crawled:
                request_urls.append(asn.prefix_url)

        return request_urls


    def parse_domain(self, response):
        # open_in_browser(response)
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)


        domain = DomainItem()

        as_number = response.xpath('//*[@id="netinfo"]/table/tbody//a/text()').extract_first()

        try:
            ip_prefix = response.xpath('//*[@id="dns"]/table/tbody')
        except:
            return
        result = {}
        for row in ip_prefix.xpath('./tr'):
            ip = row.xpath('.//a/text()').extract_first()
            result[ip] = []
            for domain in row.xpath('./td[3]/a/text()'):
                result[ip].append(domain.extract())

        yield {
                'url': response.url,
                'as_number': as_number,
                'result': result
                }


