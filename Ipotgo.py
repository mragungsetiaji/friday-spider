from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import datetime 

class Emiten(object):
    
    def __init__(self, emitenCode, emitenName):
        self.emitenCode = emitenCode
        self.emitenName = emitenName
        self.soup = None
        self.getSoup()

        self.date = datetime.datetime.now()

        # Price Details
        self.lastPrice = None
        self.prevPrice = None
        self.lotPrice = None
        self.chgPrice = None
        self.highPrice = None
        self.valPrice = None
        self.precentPrice = None
        self.lowPrice = None
        self.AvgPrice = None
        self.getTopOrderBook()

        # Price Orderbook
        self.listBidOff = None
        self.sumBidLot = None
        self.sumOffLot = None
        self.orderBookToList()

        # Summary
        self.listSummary = []
        self.getEmitenToList()

    def getSoup(self):
        homepage = "https://www.indopremier.com/ipotgo/newsSmartSearch.php?code="
        page = urlopen(homepage + self.emitenCode)
        self.soup = BeautifulSoup(page, "html.parser")

    ## Top Orderbook Section
    def getLastPrice(self):
        last = self.soup.find("tr", attrs={"class":"semibold text-up"})
        last = last.text.strip()
        self.lastPrice = int(last[8:])

    def getTopOrderBook(self):
        tbl = self.soup.find("table", attrs={"class":"table table-orderbook noborder mb5"})
        
        self.lastPrice = self.getExtractTbl(tbl, "Prev")
        self.prevPrice = self.getExtractTbl(tbl, "Open")
        self.lotPrice = self.getExtractTbl(tbl, "Lot")
        self.chgPrice = self.getExtractTbl(tbl, "Chg")
        self.highPrice = self.getExtractTbl(tbl, "High")
        self.valPrice = self.getExtractTbl(tbl, "Val")
        self.precentPrice = self.getExtractTbl(tbl, "%")
        self.lowPrice = self.getExtractTbl(tbl, "Low")
        self.AvgPrice = self.getExtractTbl(tbl, "Avg")

    def getExtractTbl(self, tbl, text):
        strToFind = tbl.find("td", text=text)
        strToFind = strToFind.findNext("td")
        return strToFind.text.strip()

    ## Bot Orderbook Section (biddoffer)
    def getBotOrderBook(self):
        return self.soup.find("table", attrs={"class":"table table-orderbook bidoffer noborder nm"})

    def getParseTable(self):
        table = self.getBotOrderBook()
        """ Get data from table """
        return pd.DataFrame([
            [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
                for row in table.find_all('tr')
        ])
    
    def orderBookToList(self):
        '''
            Membuat orderbook menjadi list dan total lot order
            return:
                listBidOff = list dari orderbook
                sumBidLot = total lot dari bid
                sumOffLot = total lot dari offer
        '''
        dt = self.getParseTable()

        self.listBidLot, self.listBidPrice, self.listOffPrice, self.listOffLot = [], [], [], []
        for i1 in range(1, 11): 
            self.listBidLot.append(dt[1][i1])
            self.listOffLot.append(dt[4][i1])

            self.listBidPrice.append(dt[2][i1])
            self.listOffPrice.append(dt[3][i1])

        self.sumBidLot = dt[1][11]
        self.sumOffLot = dt[3][11]

    # Summary Section
    def getEmitenToList(self):
        self.listSummary.append(self.emitenCode)
        self.listSummary.append(self.emitenName)
        self.listSummary.append(self.date)

        self.listSummary.append(self.lastPrice)
        self.listSummary.append(self.prevPrice)
        self.listSummary.append(self.lotPrice)
        self.listSummary.append(self.chgPrice)
        self.listSummary.append(self.highPrice)
        self.listSummary.append(self.valPrice)
        self.listSummary.append(self.precentPrice)
        self.listSummary.append(self.lowPrice)
        self.listSummary.append(self.AvgPrice)

        for price in self.listBidLot:
            self.listSummary.append(price)
        
        for price in self.listBidPrice:
            self.listSummary.append(price)
        
        for price in self.listOffPrice:
            self.listSummary.append(price)
        
        for price in self.listOffLot:
            self.listSummary.append(price)

        self.listSummary.append(self.sumBidLot)
        self.listSummary.append(self.sumOffLot)

def readEmitenData(csv):
    csv = pd.read_csv(csv)
    allEmiten = []

    headerList = ["emitenCode", "emitenName", "Date",
        "lastPrice", "prevPrice", "lotPrice", "chgPrice", "highPrice", "valPrice", "precentPrice", "lowPrice", "AvgPrice",
        "BidLot1","BidLot2","BidLot3","BidLot4","BidLot5","BidLot6","BidLot7","BidLot8","BidLot9","BidLot10",
        "BidPrice1","BidPrice2","BidPrice3","BidPrice4","BidPrice5","BidPrice6","BidPrice7","BidPrice8","BidPrice9","BidPrice10",
        "OffPrice1","OffPrice2","OffPrice3","OffPrice4","OffPrice5","OffPrice6","OffPrice7","OffPrice8","OffPrice9","OffPrice10",
        "OffLot1","OffLot2","OffLot3","OffLot4","OffLot5","OffLot6","OffLot7","OffLot8","OffLot9","OffLot10",
        "sumBidLot", "sumOffLot"]

    for index in csv.index:
        emitenCode = csv["Kode"][index]
        emitenName = csv["Nama Emiten"][index]

        try:
            emitenData = Emiten(emitenCode, emitenName) 
            allEmiten.append(emitenData.listSummary)
            print("Process " + str(round(index/len(csv.index), 2) * 100) + "%, " +
                "Saham " + str(csv["Kode"][index]) + " berhasil didownload")
        except Exception:
            print("Saham "+ str(csv["Kode"][index]) + " tidak berhasil didownload")
            pass

    return pd.DataFrame(allEmiten, columns=headerList)
