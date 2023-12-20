import os
import pymongo

API_KEY = os.getenv('API_KEY')
PY_MONGO_CLIENT = pymongo.MongoClient(os.getenv('MONGO_CONNECTION_STRING'))
#EXCHANGE_LS = ['NASDAQ', 'NYSE', 'LSE', 'JPX', 'HKSE', 'NSE', 'ASX', 'TSX', 'EURONEXT','XETRA']
EXCHANGE_LS = ['PNK']