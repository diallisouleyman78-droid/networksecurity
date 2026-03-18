from networksecurity.constants.training_pipeline import SAVED_MODEL_DIR, MODEL_FILE_NAME

import os, sys

from networksecurity.exception import NetworkSecurityException
from networksecurity.logging import logging

class NetworkModel:
    def __init__(self, preprocessor,model):
        try:
            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def predict(self, X):
        try:
            X_transformed = self.preprocessor.transform(X)
            y_hat = self.model.predict(X_transformed)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e    