# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy.utils.project import get_project_settings

class BrokerSummarySpider(scrapy.Spider):
    
    name = 'broker_summary_spider'
    code = 'ANTM'

    def start_requests(self):

        settings = get_project_settings()

        start= '08/19/2020'
        end='08/19/2020'
        fd='all'
        board='all'

        endpoint = settings["BROKERSUMMARY_ENDPOINT_URL"]
        url = '{}?code={}&start={}&end={}&fd={}&board={}'.format(
            endpoint, self.code, start, end, fd, board
        )

        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        
        xpath = '//*[@class="table table-summary table-hover noborder nm"]//tbody/tr'
        for row in response.xpath(xpath):
            
            yield {
                'emiten': self.code,
                'buyer_code' : row.xpath('td[1]//text()').extract_first(),
                'buyer_lot': row.xpath('td[2]//text()').extract_first(),
                'buyer_value' : row.xpath('td[3]//text()').extract_first(),
                'buyer_average' : row.xpath('td[4]//text()').extract_first(),
                'seller_code' : row.xpath('td[6]//text()').extract_first(),
                'seller_lot': row.xpath('td[7]//text()').extract_first(),
                'seller_value' : row.xpath('td[8]//text()').extract_first(),
                'seller_average' : row.xpath('td[9]//text()').extract_first()
            }

        pass


