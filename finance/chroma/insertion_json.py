import json
from tqdm import tqdm
from finance.params import *
from finance.mongo.extraction import *
import os

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from langchain_community.document_loaders import JSONLoader


def insert_local_json(base_path:str):
    
    def json_to_loader(path: str) -> list:
        
        """return a loader object from a json file"""
        
        def metadata_func(record: dict, metadata: dict) -> dict:
        
            metadata["symbol"] = record.get("symbol")
            metadata["quarter"] = record.get("quarter")
            metadata['year'] = record.get("year")
            metadata['date'] = record.get("date")

            return metadata
        
        loader = JSONLoader(file_path=path, jq_schema= '.[].[]',text_content=False, metadata_func=metadata_func, content_key="content")
        collection = loader.load()
        
        return collection

    def insert_chroma(data:list, client: str = 'localhost', port: int = 8083):
        
        """reform the data into the chroma format and insert it into the chroma database"""
        
        chroma_client = chromadb.HttpClient(host=client, port = port, settings=Settings(allow_reset=True, anonymized_telemetry=False))
    
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        collection = chroma_client.get_or_create_collection(name="transcripts_mililm_l6_v3", embedding_function=sentence_transformer_ef)
        
        documents = [i.page_content for i in data]
        ids = [str(i.metadata['year'])+'Q'+str(i.metadata['quarter'])+i.metadata['symbol'] for i in data]
        metadatas = [i.metadata for i in data]
        
        print(len(documents))
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids)
        
        return None
        
    json_ls = os.listdir(base_path)
    
    json_ls = [base_path+i for i in json_ls]
    
    json_loop = tqdm(json_ls)
    
    for js in json_loop:
                
        #json_loop.set_postfix_str(f"current: {ticker}")
        
        collection = json_to_loader(js)
        
        if len(collection) > 0:
        
            insert_chroma(collection)
            
            
if __name__  == '__main__':
    
    insert_local_json('json_data/')
    
    