import os, sys
from xml.parsers.expat import model

from networksecurity.exception import NetworkSecurityException
from networksecurity.logging import logging

from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact

from networksecurity.utils.main_utils.utils import save_object, load_object, evaluate_model
from networksecurity.utils.main_utils.utils import load_numpy_array_data

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import r2_score

from dotenv import load_dotenv
load_dotenv()

import mlflow
import mlflow.sklearn
import dagshub

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
EXPERIMENT_NAME = "NetworkSecurity-Phishing-Detection"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

dagshub.init(repo_owner='diallisouleyman78', repo_name='networksecurity', mlflow=True)


class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def track_mlflow(self, best_model, classification_metric, run_name="train"):
        with mlflow.start_run(run_name=f"model_training_{run_name}"):
            mlflow.log_param("model_type", best_model.__class__.__name__)
            mlflow.log_metric("f1_score", classification_metric.f1_score)
            mlflow.log_metric("precision_score", classification_metric.precision_score)
            mlflow.log_metric("recall_score", classification_metric.recall_score)
            mlflow.sklearn.log_model(best_model, "model")
        
    def train_model(self, x_train, y_train, x_test, y_test):   
        models = {
            "Logistic Regression": LogisticRegression(verbose=1),
            "Random Forest": RandomForestClassifier(verbose=1),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "AdaBoost": AdaBoostClassifier(),
            "Decision Tree": DecisionTreeClassifier(),
            "KNN": KNeighborsClassifier()
        }
        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy', 'log_loss'],
            },

            "Random Forest": {
                'n_estimators': [8, 16, 32, 64, 128, 256]
            },
            "Gradient Boosting": {
                'learning_rate': [0.1, 0.01, 0.05],
                'n_estimators': [8, 16, 32, 64, 128, 256]
            },

            "Logistic Regression": {},

            "AdaBoost": {
                'learning_rate': [0.1, 0.01, 0.05],
                'n_estimators': [8, 16, 32, 64, 128, 256]
            },

            "KNN": {
                'n_neighbors': [5, 7, 9, 11, 13, 15]
            }
        }

        model_report: dict = evaluate_model(x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test, models=models, params=params)
        
        ##best model score from the dict
        best_model_score = max(sorted(model_report.values()))
        ##best model name from the dict
        best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]

        best_model = models[best_model_name]
        y_train_pred = best_model.predict(x_train)
        
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)
        

        ## Track MLFLOW
        self.track_mlflow(best_model, classification_train_metric, run_name="train")


        y_test_pred = best_model.predict(x_test)
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
        self.track_mlflow(best_model, classification_test_metric, run_name="test")

        preprocessor = load_object(self.data_transformation_artifact.transformed_object_file_path)
        model_dir = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir, exist_ok=True)

        NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path, obj=NetworkModel)
        #save the model to the file path specified in the model trainer config using the save_object function from the utils module which uses pickle to save the model object to the file path specified in the model trainer config. We are saving the model object which contains both the preprocessor and the model because we want to use the preprocessor and the model together for prediction in the future. If we save only the model, then we will have to load the preprocessor separately and then use it for prediction which will be time consuming and we have already done the data transformation in the data transformation stage. So we will save both the preprocessor and the model together in a single object and save that object to the file path specified in the model trainer config.

        save_object("final_model/model.pkl", best_model)

        ##model trainer artifact
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )
        logging.info(f"Best model found on both training and testing dataset: {best_model_name} with test score: {best_model_score}")
        return model_trainer_artifact

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training ant testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path) # we do it this way because we want to load the transformed data which is in numpy array format and we want to use it for training the model and evaluating the model. If we load the original data which is in csv format, then we will have to do the data transformation again which will be time consuming and we have already done the data transformation in the data transformation stage. So we will load the transformed data which is in numpy array format and use it for training the model and evaluating the model.

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1]
            )

            model = self.train_model(x_train, y_train, x_test, y_test)
            return model
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e