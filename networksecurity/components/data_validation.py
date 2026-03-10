from networksecurity.entity.artifact_entity import DataValidationArtifact, DataIngestionArtifact
from networksecurity.exception import NetworkSecurityException
from networksecurity.logging import logging
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.constants import SCHEMA_FILE_PATH  # schema path comes from general constants
from scipy.stats import ks_2samp  # Kolmogorov-Smirnov test for distribution comparison
import os, sys
import pandas as pd
from networksecurity.utils.main_utils import read_yaml_file # for reading the yaml file which contains the schema of the data
from networksecurity.utils.main_utils import write_yaml_file # for writing the yaml file which contains the drift report of the data

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH) # read the schema.yaml file which contains the schema of the data
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    @staticmethod # used to define a static method which does not require an instance of the class to be called
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path) # read the data from the file path and return a dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self.schema_config["columns"]) # get the number of columns from the schema.yaml file
            if len(dataframe.columns) == number_of_columns: # check if the number of columns in the dataframe is equal to the number of columns in the schema.yaml file
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)    
        
    def is_numerical_column_exist(self, dataframe: pd.DataFrame) -> bool:
        try:
            numerical_columns = self.schema_config["numerical_columns"] # get the list of numerical columns from the schema.yaml file
            for num_col in numerical_columns: # check if each numerical column exists in the dataframe
                if num_col not in dataframe.columns:
                    return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def check_data_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2) # perform the Kolmogorov-Smirnov test to check if the train and test data are from the same distribution
                if threshold <= is_same_dist.pvalue: # if the p-value is less than or equal to the threshold, then we can say that the train and test data are from the same distribution
                    is_found = True
                else:
                    is_found = False
                    status = False
                report.update({column: {"p_value": float(is_same_dist.pvalue), "drift_status": is_found, "same_distribution": is_found}}) # update the report with the p-value and the same distribution status for
            drift_report_file_path = self.data_validation_config.drift_report_dir
            dir_path = os.path.dirname(drift_report_file_path) # get the directory path from the drift report file path
            os.makedirs(dir_path, exist_ok=True) # create the directory
            write_yaml_file(file_path=drift_report_file_path, data=report) # write the report to the drift report file path


        except Exception as e:
            raise NetworkSecurityException(e, sys)
        



    def initiate_data_validation(self) -> DataValidationArtifact: # always specify the return type    
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path # get the train and test file paths from the data ingestion artifact

            ## read the data from the train and test file paths
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            ## validate the number of columns in the train and test dataframes
            status = self.validate_number_of_columns(dataframe=train_dataframe) # validate the number of columns in the train dataframe
            if not status:
                error_message = f"Train dataframe does not have the expected number of columns." # if the number of columns in the train dataframe is not equal to the number of columns in the schema.yaml file, then we can log an error message and return a data validation artifact with the validation status as False.

            status = self.validate_number_of_columns(dataframe=test_dataframe) # validate the number of columns in the test dataframe
            if not status:
                error_message = f"Test dataframe does not have the expected number of columns." # if the number of columns in the test dataframe is not equal to the number of columns in the schema.yaml file, then we can log an error message and return a data validation artifact with the validation status as False.

            ##validate the presence of numerical columns in the train and test dataframes
            status = self.is_numerical_column_exist(dataframe=train_dataframe) # validate the presence of numerical columns in the train dataframe
            if not status:
                error_message = f"Train dataframe does not have all the numerical columns." # if any of the numerical columns are not present in the train dataframe, then we can log an error message and return a data validation artifact with the validation status as False.    

            status = self.is_numerical_column_exist(dataframe=test_dataframe) # validate the presence of numerical columns in the test dataframe
            if not status:
                error_message = f"Test dataframe does not have all the numerical columns." # if any of the numerical columns are not present in the test dataframe, then we can log an error message and return a data validation artifact with the validation status as False.    

            ## check data drift using the Kolmogorov-Smirnov test
            status = self.check_data_drift(base_df=train_dataframe, current_df=test_dataframe) # check data drift between the train and test dataframes
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path) # get the directory path from the valid train file path
            os.makedirs(dir_path, exist_ok=True) # create the directory for the valid train file if it does not exist
            

            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True) # save the valid train dataframe to the valid train file path
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True) # save the valid test dataframe to the valid test file path

            data_validation_artifact = DataValidationArtifact(validation_status=status,
                                                               valid_train_file_path=self.data_validation_config.valid_train_file_path,
                                                               valid_test_file_path=self.data_validation_config.valid_test_file_path,
                                                               invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                                                               invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                                                               drift_report_file_path=self.data_validation_config.drift_report_dir) # create a data validation artifact object to store the validation status and the file paths of the valid and invalid train and test data and the drift report file path

            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)