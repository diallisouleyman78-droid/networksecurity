from datetime import datetime
import os
from networksecurity.constants import (
    training_pipeline,
    DATA_VALIDATION_DIR_NAME,
    DATA_VALIDATION_DIR,
    DATA_VALIDATION_INVALID_DIR,
    DATA_VALIDATION_DRIFT_REPORT_DIR,
    DATA_VALIDATION_DRIFT_REPORT_FILE_NAME,
)

# debugging prints (can be removed later)
print(training_pipeline.PIPELINE_NAME)
print(training_pipeline.ARTIFACT_DIR)


class TrainingPipelineConfig:
    def __init__(self, timestamp=datetime.now()):
        timestamp = timestamp.strftime("%Y_%m_%d_%H_%M_%S")
        self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        self.model_dir = os.path.join("final_model")
        self.timestamp = timestamp


class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        # from training_pipeline_config we will get the artifact_dir and then we will create a data_ingestion_dir inside it
        self.data_ingestion_dir = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_INGESTION_DIR_NAME,
        )

        self.feature_store_dir = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,
            training_pipeline.FILE_NAME,
        )

        self.training_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TRAIN_FILE_NAME,
        )

        self.testing_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TEST_FILE_NAME,
        )

        self.train_test_split_ratio: float = (
            training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        )
        self.collection_name: str = (
            training_pipeline.DATA_INGESTION_COLLECTION_NAME
        )
        self.database_name: str = (
            training_pipeline.DATA_INGESTION_DATABASE_NAME
        )


class DataValidationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        """Configuration for the data validation stage.

        Paths are built off the pipeline's artifact directory using constants
        from the *root* constants module.  The training_pipeline submodule only
        contains ingestion-specific values, so we import the validation
        identifiers separately above.
        """

        self.data_validation_dir = os.path.join(
            training_pipeline_config.artifact_dir,
            DATA_VALIDATION_DIR_NAME,
        )

        self.valid_data_dir = os.path.join(self.data_validation_dir, DATA_VALIDATION_DIR)
        self.invalid_data_dir = os.path.join(self.data_validation_dir, DATA_VALIDATION_INVALID_DIR)

        self.valid_train_file_path = os.path.join(
            self.valid_data_dir, training_pipeline.TRAIN_FILE_NAME
        )
        self.valid_test_file_path = os.path.join(
            self.valid_data_dir, training_pipeline.TEST_FILE_NAME
        )

        self.invalid_train_file_path = os.path.join(
            self.invalid_data_dir, training_pipeline.TRAIN_FILE_NAME
        )
        self.invalid_test_file_path = os.path.join(
            self.invalid_data_dir, training_pipeline.TEST_FILE_NAME
        )

        self.drift_report_dir = os.path.join(
            self.data_validation_dir,
            DATA_VALIDATION_DRIFT_REPORT_DIR,
            DATA_VALIDATION_DRIFT_REPORT_FILE_NAME,
        )


class DataTransformationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_transformation_dir = os.path.join(training_pipeline_config.artifact_dir, training_pipeline.DATA_TRANSFORMATION_DIR_NAME)
        self.transformed_train_file_path = os.path.join(self.data_transformation_dir, training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR, training_pipeline.TRAIN_FILE_NAME.replace(".csv", ".npy"))
        self.transformed_test_file_path = os.path.join(self.data_transformation_dir, training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR, training_pipeline.TEST_FILE_NAME.replace(".csv", ".npy"))
        self.transformed_object_file_path = os.path.join(self.data_transformation_dir, training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR, training_pipeline.PREPROCESSING_OBJECT_FILE_NAME)


class ModelTrainerConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.model_trainer_dir = os.path.join(training_pipeline_config.artifact_dir, training_pipeline.MODEL_TRAINER_DIR_NAME)
        self.trained_model_file_path = os.path.join(self.model_trainer_dir, training_pipeline.MODEL_TRAINER_TRAINED_MODEL_DIR, training_pipeline.MODEL_FILE_NAME)
        self.expected_accuracy = training_pipeline.MODEL_TRAINER_EXPECTED_SCORE
        self.over_fitting_under_fitting_threshold = training_pipeline.MODEL_TRAINER_OVER_FITTING_UNDER_FITTING_THRESHOLD