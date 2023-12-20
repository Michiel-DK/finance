import os
import pymongo
import pandas as pd
import numpy as np
import requests

from finance.params import *


def query_mongodb(exchange_ls:list, table:str, **kwargs) -> list:
    
    """
    Get all tickers from mongo_db
    ----
    exchange_ls = list of exchanges to filter (give empty list for all)
    """
    client = PY_MONGO_CLIENT
    collection = client['finance'][table]
    
    if len(exchange_ls) > 0:
    
        # Query to filter documents based on the "my_key" field
        query = {"$and": [
        {"exchangeShortName": {"$in": exchange_ls}},
        
            kwargs
        ]}
    
    else:
        query = kwargs

    # Fetch documents that match the query
    result = list(collection.find(query))
    print(f'exchange {kwargs} - {len(result)}')
    return result


if __name__ == '__main__':
    
    #all_tickers
    echange_ls = EXCHANGE_LS
    table_name = 'all_tickers'
    kwargs = {'type':'stock'}
    
    result = query_mongodb(echange_ls, table_name , **kwargs)
    
    print(len(result))