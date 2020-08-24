# -*- coding: utf-8 -*-
import scrapy

class BrokerSummaryItem(scrapy.Item):

    _id = scrapy.Field()
    date = scrapy.Field()
    emiten = scrapy.Field()
    type = scrapy.Field()
    broker_code = scrapy.Field()
    lot = scrapy.Field()
    value = scrapy.Field()
    average = scrapy.Field()