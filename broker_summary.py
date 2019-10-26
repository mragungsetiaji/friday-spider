#%%
import requests
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from config import BROKER_SUMMARY_ENDPOINT

#%%
column = [
    "buyer", "buyer_lot", "buyer_val", "buyer_avg", "#",
    "seller", "seller_lot",	"seller_val", "seller_Avg"
]

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
    df["val"] = df["lot"]*df["avg"]

    return df
#%%
if __name__ == "__main__":

    # Get today data
    code = "BBRI"
    date = "10/24/2019"

    #date = datetime.date.today().strftime("%m/%d/%Y")

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
    df.insert(0, "date", date)
    
    print(df)


