import os
from dotenv import load_dotenv
import sys
import json
import pandas as pd
import numpy as np
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import certifi # used to provide a certificate bundle for secure connections

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

ca = certifi.where() # Get the path to the certificate bundle


class NetworkDataExtract():
    def __init___(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(inplace=True, drop=True) ## reset index and drop old index
            records = list(json.loads(data.T.to_json()).values()) ## convert dataframe to json and load it as a list of records
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def insert_data_to_mongo(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca) ## create a MongoDB client with the provided URL

            self.database = client[self.database] ## access the specified database
            self.collection = self.database[self.collection] ## access the specified collection
            self.collection.insert_many(self.records) ## insert the records into the collection

            return(len(self.records))

        except Exception as e:
            raise NetworkSecurityException(e, sys)

if __name__ == "__main__":

    FILE_PATH = "Network_Data/phisingData.csv"
    DATABASE = "Diallo_Network_Security"
    collection = "PhishingData"
    networkobj = NetworkDataExtract()

    records = networkobj.csv_to_json(file_path=FILE_PATH)
    print(records)
    no_of_records = networkobj.insert_data_to_mongo(records, DATABASE, collection)

    print(f"{no_of_records} records inserted successfully into MongoDB collection: {collection}")
