# -*- coding: utf-8 -*-
import scrapy
from bgp_bots.spiders import BaseSpider
from bgp_bots.items import ASNItem
from scrapy_splash import SplashRequest, SlotPolicy

from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network





class BgpspiderSpider(BaseSpider):
    name = 'BGPSpider'
    allowed_domains = ['bgp.he.net']
    urls = [
        'https://bgp.he.net/AS4134',
        'https://bgp.he.net/search?search%5Bsearch%5D=telecom&commit=Search'
        ]
    custom_settings = {
        'ITEM_PIPELINES': {
            'bgp_bots.pipelines.DuplicatesPipeline': 300,
            # 'bgp_bots.pipelines.JsonWritePipeline': 301,
            'bgp_bots.pipelines.DjangoASNPipeline': 302,
        }
    }


    def start_requests(self):
        for url in self.urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint='execute',
                args={
                    'lua_source': self.lua_script
                },
                slot_policy=SlotPolicy.SCRAPY_DEFAULT
            )




    def parse(self, response):



        if 'search' in response.url:
            items = self.parse_search(response)
            # yield next request
            self.logger.info('Have %d domain item need crawl on SEARCH', len(items))

            for item in items:
                yield item
        else:
            items = self.parse_asn(response)
            # TODO yield Request
            self.logger.info('Have %d domain item need crawl on AS', len(items))

            for item in items:
                yield item



    def parse_asn(self, response):
        # 45 item
        items = []

        self.logger.info('on parse ASN, URL %s', response.url)

        self._save_resopnse_to_html(response)

        as_number = response.xpath('//h1/a/text()').re(r'AS\d+')[0]
        table = response.xpath('//*[@id="table_prefixes4"]/tbody/tr')


        for row in table:
            asn_item = ASNItem()
            asn_item['ip_prefix'] = row.xpath('./td[1]/a/text()').extract_first()
            asn_item['company'] = row.xpath('./td[2]/text()').extract_first().strip('\t').strip('\n')
            # self.logger.warning('Company name is %s', company_name)
            asn_item['prefix_url'] = response.urljoin(row.xpath('./td[1]/a/@href').extract_first())

            items.append(asn_item)


        # self._next_request(next_request[:1])

        return items


    def parse_search(self, response):
        # 49 item
        items = []
        self.logger.info('on parse SEARCH, URL %s', response.url)
        companys = ['China Telecom', 'China Telecom Backbone']

        table = response.xpath('//*[@id="search"]/table/tbody/tr')

        # self._save_resopnse_to_html(response)

        for row in table:

            ip = row.xpath('./td[1]/a/text()').extract_first()
            company_name = row.xpath('./td[2]/text()').extract_first()


            try:
                if company_name in companys:
                    # self.logger.warning('Company name is %s', company_name)
                    asn_item = ASNItem()
                    if isinstance(ip_network(ip), IPv4Network):
                        # self.logger.warning(ip)
                        asn_item['ip_prefix'] = ip
                    elif isinstance(ip_network(ip), IPv6Network):
                        # self.logger.warning(ip)
                        asn_item['ip_prefix'] = ip
                    else:
                        self.logger.warning(ip)
                        continue
                    asn_item['company'] = company_name
                    asn_item['prefix_url'] = response.urljoin(row.xpath('./td[1]/a/@href').extract_first())
                else:
                    continue
            except Exception as e:
                self.logger.warning(e)
                continue

            items.append(asn_item)

        # self._next_request(next_request[:1])

        return items




