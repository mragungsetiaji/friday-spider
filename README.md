# idxstock
Webscraping untuk mendapatkan data saham di IDX

broker yang digunakan untuk versi ini adalah IPOT

ada dua section dari data yang di ambil:
  - Top Orderbook
    Untuk menggunakan top orderbook:
    
    ```python
    test = Ipotgo("bbri")
    # Untuk mendapatkan harga Open
    print(test.get_top_od("Open"))
    ```
    
  - Bot Orderbook
    Untuk mendapatkan table bid-offer dalam bentuk dataframe:
    
    ```python
    test = Ipotgo("bbri")
    print(test.parse_table())
    ```
  
TODO: Record in csv for all stock listed
