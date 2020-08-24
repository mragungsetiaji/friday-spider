# -*- coding: utf-8 -*-
import scrapy
import json

from datetime import date, timedelta
from scrapy.utils.project import get_project_settings
from items.broker_summary import BrokerSummaryItem

class BrokerSummarySpider(scrapy.Spider):
    
    name = 'broker_summary_spider'
    number_of_day = 1
    traders = ["all", "f", "d"]
    board='all'
    code = 'ANTM'

    def get_date(self):

        today = date.today()
        date_range = [today - timedelta(days=i) for i in range(self.number_of_day)]

        return date_range

    def start_requests(self):

        settings = get_project_settings()
        date_range = self.get_date()

        endpoint = settings["BROKERSUMMARY_ENDPOINT_URL"]
        for datex in date_range:
            for trader in self.traders:
                url = '{}?code={}&start={}&end={}&fd={}&board={}'.format(
                    endpoint, 
                    self.code, 
                    datex.strftime("%m/%d/%Y"), 
                    date_range[0].strftime("%m/%d/%Y"), 
                    trader, 
                    self.board
                )

                yield scrapy.Request(url, 
                                    callback=self.parse, 
                                    meta={'date':datex})

    def parse(self, response):
        
        xpath = '//*[@class="table table-summary table-hover noborder nm"]//tbody/tr'
        for index, row in enumerate(response.xpath(xpath)):
            for transaction_type in ["B", "S"]:
                if transaction_type == "B":
                    broker_code=row.xpath('td[1]//text()').extract_first()
                    lot=row.xpath('td[2]//text()').extract_first()
                    value=row.xpath('td[3]//text()').extract_first()
                    average=row.xpath('td[4]//text()').extract_first()
                    
                elif transaction_type == "S":
                    broker_code=row.xpath('td[6]//text()').extract_first()
                    lot=row.xpath('td[7]//text()').extract_first()
                    value=row.xpath('td[8]//text()').extract_first()
                    average=row.xpath('td[9]//text()').extract_first()

                item = BrokerSummaryItem(
                    _id="{}-{}-{}-{}".format(
                        self.code,
                        response.meta['date'].strftime("%Y-%m-%d"),
                        transaction_type,
                        index
                    ),
                    date=response.meta['date'].strftime("%Y-%m-%d"),
                    emiten=self.code,
                    type=transaction_type,
                    broker_code=broker_code,
                    lot=lot,
                    value=value,
                    average=average
                )

                yield item
