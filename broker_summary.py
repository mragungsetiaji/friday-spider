#%%
import requests
import pandas as pd
import datetime
import logging
import re
from datetime import timedelta, date
from bs4 import BeautifulSoup
from config import BROKER_SUMMARY_ENDPOINT

#%%
column = [
    "buyer", "buyer_lot", "buyer_val", "buyer_avg", "#",
    "seller", "seller_lot",	"seller_val", "seller_Avg"
]
logging.basicConfig(level=logging.INFO)

def request(code, start, end, fd, board):
    """

        params:
            - code : emiten code
            - start : start date
            - end : end date
            - fd : foreign or domestic summary
                all=all, F=Foreign, D=Domestic
            - board : 
                all=all, RG=Regular, NG=Negotiation, TN=Tunai
    """
    data = requests.get(BROKER_SUMMARY_ENDPOINT.format(code, start, end, fd, board))
    
    return data.text


def transform(data):

    # Transform text response to dataframe
    soup = BeautifulSoup(data, features="lxml")
    table = soup.find("table", attrs={"class":"table table-summary table-hover noborder nm"})
    table_html = "<table>{}</table>".format(table.findAll('tbody')[0])
    df = pd.read_html(table_html)[0]
    
    # Transform dataframe to rawdata 
    df.columns = column
    df_buyer = df[column[:4]]
    df_buyer.columns = ["broker", "lot", "val", "avg"]
    df_buyer["status"] = "B"

    df_seller = df[column[5:]]
    df_seller.columns = ["broker", "lot", "val", "avg"]
    df_seller["status"] = "S"

    df = pd.concat([df_buyer,df_seller])
    
    return df

#%%
def daterange(start_date, end_date):

    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def clean_lot(lot):

    if "M" in str(lot):
        number = re.findall(r"\d+\.\d+", lot)[0]

        return int(float(number)*1000000)
    else:
        return int(lot)
#%%
def download_all(code, ipo_date):
    """
        Download all data since ipo till today,
        for specifiic emiten code
    """

    def to_df(code, date):

        # All
        df_all = transform(request(code, date, date, "all", "all"))
        df_all["fd"] = "A"

        # Foreign Flow
        df_f = transform(request(code, date, date, "F", "all"))
        df_f["fd"] = "F"

        # Domestic Flow
        df_d = transform(request(code, date, date, "D", "all"))
        df_d["fd"] = "D"

        # Merge
        df = pd.concat([df_all,df_f])
        df = pd.concat([df,df_d])

        df = df.reset_index(drop=True)
        df.insert(0, "code", code)
        df.insert(0, "date", date)

        df = df.dropna()
        df["lot"] = df["lot"].apply(lambda x: clean_lot(x))
        df["val"] = df["lot"].astype("int")*df["avg"].astype("int")

        return df

    start_date = ipo_date
    end_date = datetime.date.today()

    index = 0
    for date in daterange(start_date, end_date):

        date = date.strftime("%m/%d/%Y")

        if index == 0:
            df = to_df(code, date)
        else:
            df = pd.concat([df, to_df(code, date)])
        
        logging.info("Download {} data for date: {}".format(code, date))
        index += 1

    
    df = df.reset_index(drop=True)

    return df

#%%
if __name__ == "__main__":

    # code
    code = "JPFA"
    ipo_date = datetime.date(2019,5,10)

    df = download_all(code, ipo_date)
    df.to_csv("{}_broker_summary.csv".format(code), index=False)



    

