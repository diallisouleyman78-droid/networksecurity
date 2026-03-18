from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV
import yaml 
from networksecurity.exception import NetworkSecurityException
from networksecurity.logging import logging
import sys, os
import numpy as np
import pickle
# import dill for pickeling

def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    

def write_yaml_file(file_path: str, data: dict):
    try:
        with open(file_path, 'w') as yaml_file:
            yaml.dump(data, yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e    
    
def save_numpy_array_data(file_path: str, array: np.array):
    """
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_object(file_path: str, obj: object):
    """
    Save a python object to file
    file_path: str location of file to save
    obj: object to save
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            pickle.dump(obj, file_obj)
        logging.info(f"Object saved to file: {file_path}")     
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_object(file_path: str) -> object:
    """
    Load a python object from file
    file_path: str location of file to load
    return: object loaded from file
    """
    try:
        with open(file_path, 'rb') as file_obj:
            print(file_obj)
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e #read a pickle file  

def load_numpy_array_data(file_path: str) -> np.array:
    """
    Load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded from file
    """
    try:
        with open(file_path, 'rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e # to read a numpy array file
    

def evaluate_model(x_train, y_train, x_test, y_test, models, params):
    try:
        report = {}
        for i in range(len(models)):
            model = list(models.values())[i]
            param = params[list(models.keys())[i]]

            gs = GridSearchCV(model, param, cv=3)
            gs.fit(x_train, y_train)

            model.set_params(**gs.best_params_)
            model.fit(x_train, y_train)

            y_train_pred = model.predict(x_train)
            y_test_pred = model.predict(x_test)

            train_model_score = r2_score(y_train, y_train_pred)
            test_model_score = r2_score(y_test, y_test_pred)

            report[list(models.keys())[i]] = {
                "test_score": test_model_score
            }
            return report
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e   