import os
import pymongo
import pandas as pd
import numpy as np
import requests

from finance.params import *


def get_all_tickers(exchange_ls:list) -> list:
    
    """
    Get all tickers from mongo_db
    ----
    exchange_ls = list of exchanges to filter (give empty list for all)
    """
    
    client = PY_MONGO_CLIENT
    collection = client['finance']['all_tickers']
    
    if len(exchange_ls) > 0:
    
        # Query to filter documents based on the "my_key" field
        query = {"$and": [
        {"exchangeShortName": {"$in": exchange_ls}},
            {'type':'stock'}
        ]}
    
    else:
        query = {'type':'stock'}

    # Fetch documents that match the query
    result = collection.find(query)
    
    return list(result)