from dataclasses import dataclass   # acts like a decorator and is used to create data classes. A data class is a class that is used to store data and has some additional features like automatic generation of __init__, __repr__, __eq__, etc. methods


@dataclass # information returned at the end of the data ingestion process. This information will be used in the data validation process to read the train and test data for validation. If the data ingestion process is successful, then we can proceed with the data validation process. If the data ingestion process is not successful, then we can take appropriate actions like sending an email notification to the concerned team or logging the error message in the log file.
class DataIngestionArtifact:
    train_file_path: str
    test_file_path: str #used to store the file paths of the train and test data after the data ingestion process is completed. These file paths will be used in the data transformation and model training processes to read the train and test data.


@dataclass   # information returned at the end of the data validation process. This information will be used in the model training process to check if the data is valid before training the model. If the data is not valid, then we can take appropriate actions like sending an email notification to the concerned team or logging the error message in the log file. 
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str # used to store the file path of the drift report generated after the data validation process is completed. This file path will be used in the model training process to read the drift report and check for data drift before training the model.  

@dataclass
class DataTransformationArtifact:
    transformed_object_file_path: str
    transformed_train_file_path: str
    transformed_test_file_path: str
