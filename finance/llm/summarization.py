import numpy as np

import chromadb
from chromadb.utils import embedding_functions

from chromadb.config import Settings

from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.llm import LLMChain

import pandas as pd
from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import GPT4All
from langchain.prompts import PromptTemplate

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

from langchain.chains.combine_documents.stuff import StuffDocumentsChain

local_path = (
    "llm_models/gpt4all-falcon-q4_0.gguf"  # replace with your desired local file path
)

# Callbacks support token-wise streaming
callbacks = [StreamingStdOutCallbackHandler()]

# Verbose is required to pass to the callback manager
LLM = GPT4All(model=local_path, callbacks=callbacks, verbose=True)


def instantiate_client(collection_name: str = "transcripts_mililm_l6_v2"):
    
    """instantiates client and
    --> connects to chroma db
    --> instantiates sentence embedding
    """

    chroma_client = chromadb.HttpClient(host='localhost', port = 8083, settings=Settings(allow_reset=True, anonymized_telemetry=False))

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=sentence_transformer_ef)
    
    return collection


def query_client(query_text:str, **kwargs):
    
    """queries collection and returns best 10 results"""
    
    collection = instantiate_client()
    
    results = collection.query(
    query_texts=[query_text],
    n_results=10,
    where=kwargs
    )
    
    return results

def get_texts(results:list, n:int):
    
    first_transcript = results['documents'][0][-n:]
    first_transcript_meta = results['metadatas'][0][-3:]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    
    texts = text_splitter.create_documents(first_transcript, metadatas=first_transcript_meta)
    texts = text_splitter.split_documents(texts)
    
    return texts
    
    
def map_reduce(texts):
    
        # Map
    map_template = """The following is a part of a transcript for a company. It will contain the financial performance for a specific quarter in a specific year and the outlook for next quarter.
    The documents will be seperated per quarter.
    {page_content}
    Based on this set of docs, please identify:
    - the main themes
    - biggest challenges
    - biggest success
    Helpful Answer:"""

    map_prompt = PromptTemplate(input_variables=['page_content'], template=map_template)

    #map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=LLM, prompt=map_prompt)
    
    # Reduce
    reduce_template = """The following is set of summaries for a company for a specific quarter and year.
    {page_content}
    Take these and distill it into a evaluation of the main themes, challenges and successes throughout the different quarters.
    Helpful Answer:"""

    reduce_prompt = PromptTemplate(input_variables=['page_content'], template=reduce_template)
    
    # Run chain
    reduce_chain = LLMChain(llm=LLM, prompt=reduce_prompt)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="page_content",
        #metadata={'symbol':'symbol', 'quarter':'quarter', 'year':'year'}
    )

    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=2000,
        #metadata={'symbol':'symbol', 'quarter':'quarter', 'year':'year'}
    )
    
    # Run chain
    reduce_chain = LLMChain(llm=LLM, prompt=reduce_prompt)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="page_content",
        #metadata={'symbol':'symbol', 'quarter':'quarter', 'year':'year'}
    )

    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=2000,
        #metadata={'symbol':'symbol', 'quarter':'quarter', 'year':'year'}
    )
    
    # Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        # Map chain
        llm_chain=map_chain,
        # Reduce chain
        reduce_documents_chain=reduce_documents_chain,
        # The variable name in the llm_chain to put the documents in
        document_variable_name="page_content",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
        #metadata={'symbol':'symbol', 'quarter':'quarter', 'year':'year'}
    )

    return map_reduce_chain.run(texts)



if __name__=='__main__':
    collection = instantiate_client()
    result = query_client('SHOP transcripts', **{'symbol': 'SHOP'})
    texts = get_texts(result, 3)
    output = map_reduce(texts)
    print(output)