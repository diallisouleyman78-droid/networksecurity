from datetime import datetime
import os
from networksecurity.constants import training_pipeline # folder with the __init__.py file where we have defined all the constants for the training pipeline


print(training_pipeline.PIPELINE_NAME) # we can access the constants defined in the __init__.py file using the folder name and the constant name.
print(training_pipeline.ARTIFACT_DIR)

class TrainingPipelineConfig:
    def __init__(self, timestamp=datetime.now()):
        timestamp=timestamp.strftime("%Y_%m_%d_%H_%M_%S")
        self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        self.timestamp = timestamp
   

class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig): # from training_pipeline_config we will get the artifact_dir and then we will create a data_ingestion_dir inside it
       self.data_ingestion_dir = os.path.join(training_pipeline_config.artifact_dir,training_pipeline.DATA_INGESTION_DIR_NAME) # create a data_ingestion_dir inside the artifact_dir

       self.feature_store_dir = os.path.join(self.data_ingestion_dir, training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR, training_pipeline.FILE_NAME) # create a feature_store_dir inside the data_ingestion_dir

       self.training_file_path: str = os.path.join(self.data_ingestion_dir, training_pipeline.DATA_INGESTION_INGESTED_DIR, training_pipeline.TRAIN_FILE_NAME) # create a training_file_path inside the ingested_dir

       self.testing_file_path: str = os.path.join(self.data_ingestion_dir, training_pipeline.DATA_INGESTION_INGESTED_DIR, training_pipeline.TEST_FILE_NAME) # create a testing_file_path inside the ingested_dir

       self.train_test_split_ratio: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
       self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
       self.database_name: str = training_pipeline.DATA_INGESTION_DATABASE_NAME