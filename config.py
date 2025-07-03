# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration settings."""
    DATA_FILE_PATH = os.path.join(BASE_DIR, 'data', 'Processors.xlsx')
    
    # Paths to your trained models
    FUNCTION_CLASSIFIER_PATH = os.path.join(BASE_DIR, 'models', 'processor_function_classifier.joblib')
    LABEL_ENCODER_PATH = os.path.join(BASE_DIR, 'models', 'function_label_encoder.joblib')
    WIRELESS_PREDICTOR_PATH = os.path.join(BASE_DIR, 'models', 'wireless_capabilities_predictor.joblib')