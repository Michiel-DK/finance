import requests
from tqdm import tqdm
from finance.params import *
from finance.mongo.extraction import *

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


import random


def api_transcripts(tickers:list, year:int):
    
    def api_transcript(ticker:str, year:int):
        
        url = f'https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{ticker}'
        
        params = {
            'year':year,
            'apikey': API_KEY
        }
        
        response = requests.get(url, params=params).json()
        return response
    
    def insert_chroma(data:dict, client: str = 'localhost', port: int = 8083):
        
        chroma_client = chromadb.HttpClient(host=client, port = port, settings=Settings(allow_reset=True, anonymized_telemetry=False))
    
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        collection = chroma_client.get_or_create_collection(name="transcripts_mililm_l6_v2", embedding_function=sentence_transformer_ef)
        
        documents = [i['content'] for i in data]
        ids = [str(i['year'])+'Q'+str(i['quarter'])+i['symbol'] for i in data]
        metadatas = [{'symbol':i['symbol'], 'quarter':i['quarter'], \
                    'year':i['year']}\
                for i in data]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids)
        
        return None
    
    ticker_loop = tqdm(tickers)
    
    for ticker in ticker_loop:
                
        ticker_loop.set_postfix_str(f"current: {ticker}")
                
        response = api_transcript(ticker, year)
        
        if len(response) > 0:
        
            insert_chroma(response)
        
        
if __name__  == '__main__':
    
    exchange_ls = ['PNK', 'NASDAQ', 'NYSE']
    
    table_name = 'all_tickers'
    
    years = [2024]
    
    kwargs = {'type':'stock'}
    
    result = query_mongodb(exchange_ls, table_name , **kwargs)
    
    result_df = pd.DataFrame(result)
        
    result_df.drop_duplicates(subset=['name', 'symbol'], inplace=True)
    
    tickers = result_df.symbol.to_list()
            
    for year in years:
        api_transcripts(tickers=tickers, year=year)
