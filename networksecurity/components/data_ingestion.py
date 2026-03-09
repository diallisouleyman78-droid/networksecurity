from networksecurity.exception import NetworkSecurityException
from networksecurity.logging import logging

##configuration for data ingestion config

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os, sys
import pymongo
from typing import List
from sklearn.model_selection import train_test_split # for splitting the data into train and test
import pandas as pd
import numpy as np


from dotenv import load_dotenv
load_dotenv() # load the environment variables from the .env file

MONGO_DB_URL = os.getenv("MONGO_DB_URL") # get the MongoDB URL from the environment variable


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def export_collection_as_dataframe(self):
        """
        Read data from database and export the collection as a dataframe
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find())) # convert the collection to a dataframe
            if "_id" in df.columns.to_list(): # check if the _id column exists in the dataframe
                df = df.drop(columns=["_id"], axis=1) # drop the _id column if it exists

            df.replace("na", np.nan, inplace=True) # replace the "na" values with np.nan values in the dataframe
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_dir
            dir_path = os.path.dirname(feature_store_file_path) # get the directory path from the feature store file path
            os.makedirs(dir_path, exist_ok=True) # create the feature store directory if it does not exist
            dataframe.to_csv(feature_store_file_path, index=False, header=True) # save the dataframe to the feature store directory
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(dataframe, test_size=self.data_ingestion_config.train_test_split_ratio, random_state=42) # split the data into train and test sets
            logging.info("Performed train test split on the data")
            logging.info("Exited split_data_as_train_test method of DataIngestion class")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path) # get the directory path from the training file path

            os.makedirs(dir_path, exist_ok=True) # create the ingested directory if it does not exist

            logging.info("Saving the train and test data in the ingested directory")

            # save the train and test data in the ingested directory
            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True) # save the train set to the ingested directory
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True) # save the test set to the ingested directory
            
            logging.info("Saved the train and test data in the ingested directory")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self):
        try:
           dataframe = self.export_collection_as_dataframe() # export the collection as a dataframe
           dataframe = self.export_data_into_feature_store(dataframe) # export the dataframe to the feature store directory
           dataframe = self.split_data_as_train_test(dataframe) # split the data into train and test sets and save them in the ingested directory

           data_ingestion_artifact = DataIngestionArtifact(train_file_path=self.data_ingestion_config.training_file_path, test_file_path=self.data_ingestion_config.testing_file_path) # create a data ingestion artifact object to store the file paths of the train and test data
           return data_ingestion_artifact # return the data ingestion artifact object


        except Exception as e:
            raise NetworkSecurityException(e, sys)    