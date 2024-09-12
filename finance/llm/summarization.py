from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.llm import LLMChain

import pandas as pd
from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.streaming_stdout_final_only import (FinalStreamingStdOutCallbackHandler)

from langchain.llms import GPT4All
from langchain.prompts import PromptTemplate

from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from finance.llm.transcript import TranscriptLoader


class Summarizer():
    
    def __init__(self, model_path:str = "llm_models/gpt4all-falcon-q4_0.gguf"):
        
        self.model_path = model_path
        
        self.llm = None
        
    def instantiate_llm(self):
        # Callbacks support token-wise streaming
        #callbacks = [StreamingStdOutCallbackHandler()]
        callbacks = [FinalStreamingStdOutCallbackHandler()] 

        # Verbose is required to pass to the callback manager
        llm = GPT4All(model=local_path, callbacks=callbacks, verbose=True)
        
        self.llm = llm

        
    def map_reduce(self, texts:list):
        
        # This controls how each document will be formatted. Specifically,
        document_prompt = PromptTemplate(
            input_variables=["page_content"],
            template="{page_content}"
        )
        document_variable_name = "context"

        
        prompt = PromptTemplate.from_template(
            """The following is a part of a transcript for a company containing it's financial performance.
                {context}
                Summarize the text focussing on challenges and successes and elaborate on the most important details.
                Helpful Answer:"""
        )
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)

        # We now define how to combine these summaries
        reduce_prompt = PromptTemplate.from_template(
            """You will receive a summarized text with challenges and successes for a company.
                {context}
                Firstly extract the year and quarter for which the transcript is for and list it at the top.
                Secondly based on this set of docs, please summarize and list the following:
                - main challenges
                - main successes
                Helpful Answer:"""
        )
        reduce_llm_chain = LLMChain(llm=self.llm, prompt=reduce_prompt)

        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_llm_chain,
            document_prompt=document_prompt,
            document_variable_name=document_variable_name
        )


        # collapse_documents_chain which is specifically aimed at collapsing documents BEFORE
        # the final call.
        prompt = PromptTemplate.from_template(
            "Collapse this content while keeping the most important information: {context}"
        )
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        collapse_documents_chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt=document_prompt,
            document_variable_name=document_variable_name
        )
        
        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=collapse_documents_chain,
            token_max=2000
        )
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=llm_chain,
            reduce_documents_chain=reduce_documents_chain,
        )
                
        return map_reduce_chain.invoke(texts)



if __name__=='__main__':
    
    
    dataloader = TranscriptLoader(collection_name = "transcripts_mililm_l6_v3", embedding_model = "all-MiniLM-L6-v2")
    dataloader.instantiate_client()
    
    where_dict = {'$and':[
              {'symbol': {
                       "$in": ['ABNB']}
              }, 
              {'year': {
                        "$gt": 2023}
              }]
         }
    
    result = dataloader.query_client('ABNB transcripts', n_results=1, **where_dict)
    texts = dataloader.get_texts(result, 1)
    
    
    local_path = ("llm_models/gpt4all-falcon-q4_0.gguf")
    
    sum = Summarizer(model_path=local_path)
    
    sum.instantiate_llm()
    output = sum.map_reduce(texts)
    