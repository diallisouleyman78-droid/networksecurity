import yaml 
from networksecurity.exception import NetworkSecurityException
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