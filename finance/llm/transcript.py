import numpy as np

import chromadb
from chromadb.utils import embedding_functions

from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter



class TranscriptLoader():
    
    def __init__(self, collection_name: str = "transcripts_mililm_l6_v3", embedding_model: str = "all-MiniLM-L6-v2"):
        
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        self.collection = None
        
    def instantiate_client(self):
        
        """instantiates client and
        --> connects to chroma db
        --> instantiates sentence embedding
        """

        chroma_client = chromadb.HttpClient(host='localhost', port = 8083, settings=Settings(allow_reset=True, anonymized_telemetry=False))

        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=self.embedding_model)

        collection = chroma_client.get_or_create_collection(name=self.collection_name, embedding_function=sentence_transformer_ef)
        
        self.collection = collection


    def query_client(self, query_text:str, n_results:int, **kwargs):
        
        """queries collection and returns best 10 results"""
        
        results = self.collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=kwargs
        )
        
        return results

    def get_texts(self, results:list, n:int):
            
        first_transcript = results['documents'][0][-n:]
        first_transcript_meta = results['metadatas'][0][-3:]
                
        #text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
        text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=100)
        
        texts = text_splitter.create_documents(first_transcript, metadatas=first_transcript_meta)
        texts = text_splitter.split_documents(texts)
        
        return texts