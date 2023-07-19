# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import logging
import requests
import dns.resolver
import traceback

from scrapy.exceptions import DropItem
from ipaddress import IPv4Address, ip_address
from retrying import retry
from json import JSONDecodeError
from collections import Counter

import django.db
from warehouse.models import ASN, Domain


def retry_if_fail(exception):
    print("#Retry for {}".format(exception), flush=True)
    if isinstance(exception, JSONDecodeError) or \
        isinstance(exception, TypeError) \
        :
        return True
    else:
        False


class JsonWritePipeline(object):

    def open_spider(self, spider):
        self.file = open('bgp.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class DuplicatesPipeline(object):
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        if dict(item) in self.items:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.items.append(item)
            return item


class DjangoASNPipeline(object):

    def process_item(self, item, spider):
        models = ASN()
        models.company = item['company']
        models.ip_prefix = item['ip_prefix']
        models.prefix_url = item['prefix_url']

        asn = ASN.objects.filter(ip_prefix__exact = models.ip_prefix).first()

        if asn is None:
            models.save()
        else:
            raise DropItem("Duplicate sql item fount: %s" % item['ip_prefix'])

        return item


class DjangoDomainPipeline(object):

    def __init__(self):
        self.logger_u3 = ''
        self.logger_u3 = ''
        self.logger = ''
        
        self.asn_as_numbers_update = ''
        self.ip = ''

        self.resolver = ''
        self.url_doh = ''
        self.data_doh = {}
        self.headers_doh = {}



    def dns_lookup_over_udp(self, domain):
        try:
            query_answers = self.resolver.query(domain)
        except (dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return None
        return [ rdata.address for rdata in query_answers ]



    def dns_lookup_over_https(self, domain):
        
        self.data_doh['name'] = domain
        self.data_doh['type'] = 'A' if isinstance(ip_address(self.ip), IPv4Address) else 'AAAA'
        
        r = requests.get(self.url_doh, headers=self.headers_doh, params=self.data_doh)
        result = r.json()
        answer = result.get('Answer')

        def ip_filter(ip):
            """
            filter not ip address value
            """
            ip = ip.get('data') if isinstance(ip, dict) else ip
            try:
                return True if isinstance(ip_address(ip), IPv4Address) else False
            except ValueError:
                return False

        return [ ip.get('data') for ip in answer if ip_filter(ip) ] if answer else None


    @retry(retry_on_exception=retry_if_fail, wait_random_min=3000, wait_random_max=10000)
    def dns_lookup(self, ip, domain):
        result_udp = self.dns_lookup_over_udp(domain)
        result_https = self.dns_lookup_over_https(domain)

        # match = True if Counter(result_https) == Counter(result_udp) else False

        if result_udp and ip in result_udp or result_https and ip in result_https:
            return True
        # elif result_https is None and result_udp:
        #     print('result_udp: {}, domain: {}'.format(result_udp, domain))
        #     print('result_https: {}, domain: {}'.format(result_https, domain))
        #     raise TypeError("return empty answer via https")
        # elif result_udp is None and result_https:
        #     print('result_udp: {}'.format(result_udp))
        #     print('result_https: {}'.format(result_https))
        #     raise TypeError("return empty answer via udp")
        else:
            return False




    def open_spider(self, spider):
        self.logger_u3 = logging.getLogger("urllib3")
        self.logger_u3.setLevel(logging.CRITICAL)
        self.logger = logging.getLogger(__name__)

    
        self.asn_as_numbers_update = ASN.objects.filter(as_number__isnull=True)

        self.resolver = dns.resolver.Resolver(configure=False)
        self.resolver.nameservers = ['1.1.1.1', '1.0.0.1', '8.8.8.8', '8.8.4.4']
        self.resolver.lifetime = 5

        self.url_doh = 'https://cloudflare-dns.com/dns-query'
        self.data_doh = {
                    'name': 'cloudflare.com',
                    'type': 'A'
                }
        self.headers_doh = { 'accept': 'application/dns-json' }



    def process_item(self, item, spider):
        

        if self.asn_as_numbers_update:
            self.asn_as_numbers_update.filter(ip_prefix=item['url'][23:]).update(as_number=item['as_number'])

        # [('202.168.153.188', item['result']['202.168.153.188'])] debug tuple
        for ip, domains in item['result'].items():
        # for ip, domains in [('202.168.153.27', item['result']['202.168.153.27']), ('202.168.153.28', item['result']['202.168.153.28'])]:
            self.ip = ip
            for domain in domains:
                django.db.close_old_connections()
                old = Domain.objects.filter(domain=domain)
                try:
                    new = { 'domain': domain,
                            'ip': ip,
                            'match_ip': True if self.dns_lookup(ip, domain) else False,
                            'record_type': 'A' if isinstance(ip_address(ip), IPv4Address) else 'AAAA',
                            'as_number': item['as_number'],
                            'ip_prefix': item['url'][23:] # Cut out https://bgp.he.net/net/
                        }
                except:
                    print(traceback.print_exc())
                    continue


                if not old:
                    self.logger.info("add new: {}".format(new))
                    new_obj = Domain(**new)
                    new_obj.save()
                    continue

                old_obj = old.first()   
                if len(old) > 1:
                    #TODO
                    self.logger.critical("MULTI OBJECT UNKNOW ERROR: {}".format(old))
                    continue
                elif old_obj.to_dict() == new:
                    self.logger.debug("Duplicate sql item fount: %s" % str(old_obj))
                else:
                    self.logger.info("update old: {}".format(old_obj.to_dict()))
                    self.logger.info("update new: {}".format(new))
                    old_obj.__dict__.update(**new)
                    old_obj.save()

                


        # ASN.objects.filter(prefix_url=item['url']).update(crawled=True)
        return item



class MongoPipelineDeprecated(object):


    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DATABASE')
        )

    def open_spider(self, spider):
        connect(self.mongo_uri + "/" + self.mongo_db, alias=self.mongo_db)


    def close_spider(self, spider):
        # self.client.close()
        return

    def process_item(self, item, spider):
        as_number = ''
        ASN(company=item['company'],
            ip_prefix=item['ip_prefix'],
            prefix_url=item['prefix_url'],
            as_number=as_number).save()
        return item