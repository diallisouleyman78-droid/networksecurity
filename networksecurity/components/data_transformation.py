import sys, os
from networksecurity.exception import NetworkSecurityException
from networksecurity.logging import logging
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import KNNImputer

from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.constants.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object

class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path) # read the data from the file path and return a dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def get_data_transformer_object(cls) -> Pipeline:  
        """
        initializes a knn imputer with the parameters specified in the constants file and returns a pipeline object which contains the imputer object
        """  
        logging.info("Entered get_data_transformer_object method of DataTransformation class")
        try:
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS) # initialize the imputer object with the parameters specified in the constants file
            logging.info("initialized knn imputer")
            processor: Pipeline = Pipeline(steps=[("imputer", imputer)]) # create a pipeline object which contains the imputer object
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e




    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Initiating data transformation")
        try:
            logging.info("Reading validated train and test data")
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)

        ## training dataframe
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1) # drop the target column from the train dataframe to get the input features dataframe
            target_feature_train_df = train_df[TARGET_COLUMN] # get the target column from the train dataframe
            target_feature_train_df = target_feature_train_df.replace(-1, 0) # replace the -1 with 0 in the target column of the train dataframe
        ## test dataframe
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1) # drop the target column from the test dataframe to get the input features dataframe
            target_feature_test_df = test_df[TARGET_COLUMN] # get the target column from the test dataframe
            target_feature_test_df = target_feature_test_df.replace(-1, 0) # replace the -1 with 0 in the target column of the test dataframe

            preprocessor = self.get_data_transformer_object() # get the data transformer object which is a pipeline object that contains the imputer object
            preprocessor_object = preprocessor.fit(input_feature_train_df) # fit the preprocessor object on the input features of the train dataframe
            transformed_input_train_feature= preprocessor_object.transform(input_feature_train_df) # transform the input features of the train dataframe using the preprocessor object
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df) # transform the input features of the test dataframe using the preprocessor object

            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)] # concatenate the transformed input features and the target column of the train dataframe to get the final train array
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)] # concatenate the transformed input features and the target column of the test dataframe to get the final test array

            #save the numpy arrays and the preprocessor object to the data transformation directory
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)


            #preparing the data transformation artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)    