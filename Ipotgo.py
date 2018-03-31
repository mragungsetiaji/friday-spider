from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

class Ipotgo(object):
    
    def __init__(self, emiten):
        self.emiten = emiten
        self.soup = None
        self.get_soup()

    def get_soup(self):
        homepage = "https://www.indopremier.com/ipotgo/newsSmartSearch.php?code="
        page = urlopen(homepage + self.emiten)
        self.soup = BeautifulSoup(page, "html.parser")

    def get_lastprice(self):
        last = self.soup.find("tr", attrs={"class":"semibold text-up"})
        last = last.text.strip()
        return int(last[8:])
        
    ## Top Orderbook Section
    def top_orderbook(self):
        return self.soup.find("table", attrs={"class":"table table-orderbook noborder mb5"})

    def get_top_od(self, text):
        '''
        Parameter text: 
            Prev, Open, Lot
            Chg, High, Val,
            %, Low, Avg
        '''
        od = self.top_orderbook()
        price = od.find("td", text=text)
        price = price.findNext("td")
        return price.text.strip()

    ## Bot Orderbook Section (biddoffer) 
    def bot_orderbook(self):
        return self.soup.find("table", attrs={"class":"table table-orderbook bidoffer noborder nm"})

    def parse_table(self):
        table = self.bot_orderbook()
        """ Get data from table """
        return pd.DataFrame([
            [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
                for row in table.find_all('tr')
        ])
