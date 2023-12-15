import os
import pymongo
import pandas as pd
import numpy as np
import requests

from finance.params import *


def get_all_tickers(database:str, table:str):
    
    def all_stocks():
        
        url = 'https://financialmodelingprep.com/api/v3/stock/list'

        params = {
            'apikey': API_KEY,
        }
        response = requests.get(url, params=params).json()
        
        return response
    
    def insert_tabular(ls: list):
        
        client = PY_MONGO_CLIENT

        collection = client[database][table]
                        
        collection.insert_many(ls)
        
        return None
    
    response = all_stocks()
    
    insert_tabular(response)
    
    
    # for i in response:
    #     print(i['symbol'])
    #     insert_tabular(i)
    
    

def api_key_metrics(tickers:list, database:str, table:str):
    
    """
    Saves ticker list to tabular mongo_db
    
    """

    def key_metrics(ticker:str, period:str):
        
        url = f'https://financialmodelingprep.com/api/v3/key-metrics/{ticker}'

        params = {
            'apikey': API_KEY,
            'period':period,
        }
        response = requests.get(url, params=params).json()
        return response

    def insert_tabular(ls: list):
        
        client = PY_MONGO_CLIENT

        collection = client[database][table]
                        
        collection.insert_many(ls)
        
        return None
    
    for ticker in tickers:
        
        symbol = ticker['symbol']
        
        print(symbol)
        
        response = key_metrics(symbol, period='quarter')
        
        try:
    
            insert_tabular(response)
        
        except:
            print(f'---- error for {ticker} ----')
        
        

if __name__ == '__main__':
      
    get_all_tickers('finance', 'ticker_all')