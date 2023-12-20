import requests
from tqdm import tqdm
from finance.params import *
from finance.mongo.extraction import *

import random



def api_all_tickers(database:str, table:str, EURONEXT: bool = False):
    
    """
    Function to insert tickers to mongodb
    -----
    database: db name
    table: table name
    """
    
    def all_stocks():
        
        if EURONEXT:
            url = 'https://financialmodelingprep.com/api/v3/symbol/available-euronext'
        else:
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
    
    
    

def api_key_metrics(tickers:list, database:str, table:str, period:str = 'quarter'):
    
    """
    Saves ticker list to tabular mongo_db
    ---
    tickers: list of symbols
    database: db name
    table: table name
    period: quarter or year
    
    """

    def api_metrics(ticker:str, period:str):
        
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
    
    for ticker in tqdm(tickers):
        
        symbol = ticker['symbol']
                
        response = api_metrics(symbol, period=period)
        
        try:
    
            insert_tabular(response)
        
        except:
            print(f'---- error for {ticker} ----')
    
    return None
            

def api_key_ratios(tickers:list, database:str, table:str, period:str = 'quarter'):
    
    def api_ratios(ticker:str, period:str):
        
        url = f'https://financialmodelingprep.com/api/v3/ratios/{ticker}'

        params = {
            'apikey': API_KEY,
            'period':period,
        }
        response = requests.get(url, params=params).json()
        return response
    
    def ratios_insert_tabular(ls: list):
        
        client = PY_MONGO_CLIENT

        collection = client[database][table]
                
        [resource.update({"key": resource["calendarYear"]+resource["period"]+resource["symbol"]}) for resource in ls]
        
        collection.insert_many(ls)
             
        # filters = [{"key": resource["key"]} for resource in ls]
                
        # for resource, filter_criteria in zip(ls, filters):
            
        #     collection.update_one(filter_criteria, {"$set": resource}, upsert=True)
            
                
                                
    for ticker in tqdm(tickers):
        
        symbol = ticker['symbol']
                
        response = api_ratios(symbol, period=period)
                
        try:
    
            ratios_insert_tabular(response)
        
        except Exception as e:
            print(f'---- {e} for {ticker} ----')
    
    return None

def api_company_profile(tickers:list, database:str, table:str):
    
    """
    Saves ticker list to tabular mongo_db
    ---
    tickers: list of symbols
    database: db name
    table: table name
    period: quarter or year
    
    """

    def api_profile(ticker:str):
        
        url = f'https://financialmodelingprep.com/api/v3/profile/{ticker}'

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
    
    ticker_loop = tqdm(tickers)
    
    for ticker in ticker_loop:
        
        symbol = ticker['symbol']
        
        ticker_loop.set_postfix_str(f"current: {symbol}")
                
        response = api_profile(symbol)
        
        try:
    
            insert_tabular(response)
        
        except:
            print(f'---- error for {ticker} ----')
    
    return None

if __name__ == '__main__':
      
    #get_all_tickers('finance', 'ticker_all')
    #exchange_ls = ['NASDAQ', 'NYSE', 'LSE', 'JPX', 'HKSE', 'NSE', 'ASX', 'TSX', 'EURONEXT','XETRA']
    
    #all_tickers
    echange_ls = EXCHANGE_LS
    table_name = 'all_tickers'
    kwargs = {'type':'stock'}
    
    result = query_mongodb(echange_ls, table_name , **kwargs)
    
    random.shuffle(result)
    
    #api_key_ratios(tickers, 'finance', 'key_ratio', period='quarter')
    api_company_profile(result, 'finance', 'company_profile')