from dataclasses import dataclass   # acts like a decorator and is used to create data classes. A data class is a class that is used to store data and has some additional features like automatic generation of __init__, __repr__, __eq__, etc. methods


@dataclass
class DataIngestionArtifact:
    train_file_path: str
    test_file_path: str #used to store the file paths of the train and test data after the data ingestion process is completed. These file paths will be used in the data transformation and model training processes to read the train and test data.