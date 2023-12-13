import os
import pymongo

API_KEY = os.getenv('API_KEY')
PY_MONGO_CLIENT = pymongo.MongoClient(os.getenv('MONGO_CONNECTION_STRING'))