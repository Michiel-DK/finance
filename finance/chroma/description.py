from finance.mongo.extraction import query_mongodb
from finance.params import *
import pandas as pd

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


def extract_description(exchange_ls: list, table_name: str):
    
    """Extract all descriptions from mongodb"""
    
    result = query_mongodb(exchange_ls=exchange_ls, table=table_name)
    
    result_df = pd.DataFrame(result)

    result_df.dropna(subset='description', inplace=True)
    result_df.dropna(subset=['sector', 'industry'], inplace=True)
    result_df.drop_duplicates(subset='companyName', inplace=True)
    
    result_description = result_df.to_dict('records')
    
    return result_description


def add_to_chroma(data:dict, host:str , collection_name:str , override:bool = True):
    
    """add text to chroma db"""
    
    chroma_client = chromadb.HttpClient(host="localhost", port = 8083, settings=Settings(allow_reset=True, anonymized_telemetry=False))

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    if override:
        chroma_client.delete_collection('general_profile_mililm_l6_v2')
        collection = chroma_client.create_collection(name="general_profile_mililm_l6_v2", embedding_function=sentence_transformer_ef)
    
    documents = [i['description'] for i in data]
    ids = [i['symbol'] for i in data]
    metadatas = [{'symbol':i['symbol'], 'exchangeShortName':i['exchangeShortName'], \
                'industry':i['industry'], 'sector':i['sector'], 'companyName':i['companyName']}\
            for i in data]
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids)
    
    return None

def query_description(query:str, n_results:int = 10):

    chroma_client = chromadb.HttpClient(host="localhost", port = 8083, settings=Settings(allow_reset=True, anonymized_telemetry=False))

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    collection = chroma_client.get_collection(name="general_profile_mililm_l6_v2", embedding_function=sentence_transformer_ef)

    query_results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
    
    return query_results

