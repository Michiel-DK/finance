import pymongo
from tqdm import tqdm
import pandas as pd
from finance.params import *

def update_field(df:pd.DataFrame, database:str, table:str, column_name:str):
    
    client = PY_MONGO_CLIENT
    collection = client[database][table]

    # Iterate through the DataFrame and update MongoDB documents
    for index, row in tqdm(df.iterrows()):
        filter_criteria = {"_id": row["_id"]}  # Adjust based on your document identifier
        update_data = {"$set": {column_name: row[column_name]}}  # Adjust based on your DataFrame columns

        # Use update_one to update the document
        collection.update_one(filter_criteria, update_data)