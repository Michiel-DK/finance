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
        
        import ipdb;ipdb.set_trace()
                
        collection.insert_one(ls)
        
        return None
    
    response = all_stocks()
    
    for i in response:
        print(i['symbol'])
        insert_tabular(i)
    
    

def api_key_metrics(tickers:list, database:str, table:str):
    
    """
    Saves ticker list to tabular mongo_db
    
    """

    def key_metrics(ticker:str, period:str):
        
        url = 'https://financialmodelingprep.com/api/v3/key-metrics/'

        params = {
            'apikey': API_KEY,
            'period':period,
            'ticker':ticker
        }
        response = requests.get(url, params=params).json()
        return response

    def insert_tabular(ls: list):
        
        client = PY_MONGO_CLIENT

        collection = client[database][table]
        
        import ipdb;ipdb.set_trace()
        
        collection.insert_many(ls)
        
        return None
    
    for ticker in tickers:
        
        response = key_metrics(ticker, period='quarter')
        
        insert_tabular(pd.DataFrame(response))
        

if __name__ == '__main__':
      
    get_all_tickers('finance', 'ticker_all')