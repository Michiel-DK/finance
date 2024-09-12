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
        
        # Map
        map_template = """You will receive a summarized text with challenges and successes for a company.
        {page_content}
        Firstly extract the year and quarter for which the transcript is for and list it at the top.
        Secondly based on this set of docs, please summarize and list the following:
        - main challenges
        - main successes
        Helpful Answer:"""

        map_prompt = PromptTemplate(input_variables=['page_content'], template=map_template)

        #map_prompt = PromptTemplate.from_template(map_template)
        map_chain = LLMChain(llm=self.llm, prompt=map_prompt)
        
        # Reduce
        reduce_template = """The following is a part of a transcript for a company containing it's financial performance.
        {page_content}
        Summarize the text focussing on challenges and successes.
        Helpful Answer:"""

        reduce_prompt = PromptTemplate(input_variables=['page_content'], template=reduce_template)
        
        # Run chain
        reduce_chain = LLMChain(llm=self.llm, prompt=reduce_prompt)
        
        # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="page_content"
            #metadata={'symbol':'symbol', 'quarter':'quarter', 'year':'year'}
        )

        # Combines and iteratively reduces the mapped documents
        reduce_documents_chain = ReduceDocumentsChain(
            # This is final chain that is called.
            combine_documents_chain=combine_documents_chain,
            # If documents exceed context for `StuffDocumentsChain`
            collapse_documents_chain=combine_documents_chain,
            # The maximum number of tokens to group documents into.
            token_max=1024,
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

        import ipdb; ipdb.set_trace()
        
        return map_reduce_chain.invoke(texts)



if __name__=='__main__':
    
    
    dataloader = TranscriptLoader(collection_name = "transcripts_mililm_l6_v3", embedding_model = "all-MiniLM-L6-v2")
    dataloader.instantiate_client()
    
    where_dict = {'$and':[
              {'symbol': {
                       "$in": ['TSLA']}
              }, 
              {'year': {
                        "$gt": 2023}
              }]
         }
    
    result = dataloader.query_client('TESLA transcripts', n_results=1, **where_dict)
    texts = dataloader.get_texts(result, 1)
    
    
    local_path = ("llm_models/gpt4all-falcon-q4_0.gguf")
    
    sum = Summarizer(model_path=local_path)
    
    sum.instantiate_llm()
    output = sum.map_reduce(texts)
    
    # collection = instantiate_client()
    # result = query_client('TESLA transcripts', **{'symbol': 'TSLA'})
    # texts = get_texts(result, 3)
    # output = map_reduce(texts)
    #print(output)