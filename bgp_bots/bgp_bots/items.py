# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class ASNItem(scrapy.Item):
    company = scrapy.Field()
    as_number = scrapy.Field()
    ip_prefix = scrapy.Field()
    prefix_url = scrapy.Field()

class DomainItem(scrapy.Item):
    domain = scrapy.Field()
    ip = scrapy.Field()
    record_type = scrapy.Field()
    checked = scrapy.Field()

    