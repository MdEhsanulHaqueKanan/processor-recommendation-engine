import pandas as pd
import re
import joblib
import logging
from typing import Any, Dict, List, Tuple, Optional

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# It's good practice to define column names as constants to avoid typos
COL_YEAR = 'Year Released'
COL_CORES = 'Number of processor core(s)'

def load_and_process_data(file_path: str) -> pd.DataFrame:
    """Loads and preprocesses the processor data from the given file path."""
    try:
        df_raw = pd.read_excel(file_path)
        
        def clean_numeric_column(series):
            return pd.to_numeric(series.astype(str).str.extract(r'(\d+\.?\d*)', expand=False), errors='coerce')

        def create_connectivity_features(df_in):
            df_out = df_in.copy()
            df_out['has_wifi_6_or_higher'] = df_out['Wireless LAN support'].str.contains('ax|wi-fi 6', case=False, na=False)
            df_out['has_5g'] = df_out['Supported Cellular Data Links'].str.contains('5g', case=False, na=False)
            return df_out

        columns_to_clean = [COL_CORES, 'Feature Size']
        for col in columns_to_clean:
            if col in df_raw.columns:
                df_raw[col] = clean_numeric_column(df_raw[col])
        
        df_processed = create_connectivity_features(df_raw)
        logging.info("Dataset loaded and preprocessed successfully.")
        return df_processed
    except FileNotFoundError:
        logging.error(f"Data file not found at {file_path}.")
        return pd.DataFrame()

def get_recommendations(requirements: Dict[str, Any], data: pd.DataFrame) -> pd.DataFrame:
    """Filters the dataset based on user requirements."""
    if data.empty: return pd.DataFrame()
    
    filtered_df = data.copy()
    if requirements.get('designer'):
        filtered_df = filtered_df[filtered_df['Designer'].str.lower() == requirements['designer'].lower()]
    if all(k in requirements for k in ('min_year', 'max_year')):
        filtered_df = filtered_df[filtered_df[COL_YEAR].between(requirements['min_year'], requirements['max_year'])]
    if all(k in requirements for k in ('min_cores', 'max_cores')):
        filtered_df = filtered_df[filtered_df[COL_CORES].between(requirements['min_cores'], requirements['max_cores'])]
    if requirements.get('needs_5g'):
        filtered_df = filtered_df[filtered_df['has_5g'] == True]
    if requirements.get('needs_wifi_6'):
        filtered_df = filtered_df[filtered_df['has_wifi_6_or_higher'] == True]
    
    display_columns = ['Designer', 'Serie', 'Type', COL_YEAR, COL_CORES, 'Feature Size', 'Function']
    display_columns = [col for col in display_columns if col in filtered_df.columns]
    
    result_df = filtered_df[display_columns].sort_values(by='Year Released', ascending=False)

    # Rename columns to a consistent, template-friendly format
    result_df = result_df.rename(columns={
        'Designer': 'designer',
        'Serie': 'serie',
        'Type': 'type',
        COL_YEAR: 'year_released',
        COL_CORES: 'number_of_cores',
        'Feature Size': 'feature_size',
        'Function': 'function'
    })
    return result_df


def load_ml_artifacts(function_model_path: str, encoder_path: str, wireless_model_path: str) -> Tuple[Any, Any, Any]:
    """Loads all trained models and encoders from disk."""
    try:
        # Assuming the wireless model artifact is a dict: {'model': model_obj, 'features': [...], 'output_labels': [...]}
        function_model = joblib.load(function_model_path)
        label_encoder = joblib.load(encoder_path)
        wireless_model = joblib.load(wireless_model_path)
        logging.info("All ML artifacts loaded successfully.")
        return function_model, label_encoder, wireless_model
    except FileNotFoundError as e:
        logging.error(f"Could not load ML artifact: {e}")
        return None, None, None

def predict_processor_function(model: Any, label_encoder: Any, input_data: Dict[str, Any]) -> str:
    """Predicts the function of a processor."""
    if model is None or label_encoder is None: return "Error: Model not loaded."
    try:
        input_df = pd.DataFrame([input_data])
        prediction_numeric = model.predict(input_df)
        prediction_string = label_encoder.inverse_transform(prediction_numeric)
        return prediction_string[0]
    except KeyError as e:
        logging.error(f"Error during function prediction: Missing feature in input data - {e}")
        return "An error occurred due to missing input."
    except Exception as e:
        logging.error(f"Error during function prediction: {e}")
        return "An error occurred."

def predict_wireless_features(model_artifact: Optional[Any], input_data: Dict[str, Any]) -> List[str]:
    """Predicts the wireless features of a processor."""
    if model_artifact is None:
        return []

    # Check if the artifact is a dictionary (the new, preferred format)
    # or just the model itself (the old format for backward compatibility).
    if isinstance(model_artifact, dict):
        model = model_artifact.get('model')
        required_features = model_artifact.get('features')
        output_labels = model_artifact.get('output_labels')
        if not all([model, required_features, output_labels]):
            return ["Error: Wireless model artifact is malformed."]
    else:
        # Fallback for when the raw model is passed directly.
        # This is less maintainable, but provides backward compatibility.
        model = model_artifact
        required_features = [
            'Year Released', 'Number of processor core(s)', 'Feature Size', 'GPU Clock',
            'Total L2 Cache', 'Total L3 Cache', 'Designer', 'Semiconductor Technology', 'Fab',
            'has_performance_cores', 'has_efficiency_cores'
        ]
        output_labels = ['5G Support', 'Wi-Fi 6 or higher', 'USB 3.0 or higher']

    try:
        # Create a new dictionary with only the required columns, preventing KeyErrors
        wireless_input_data = {key: input_data[key] for key in required_features}
        input_df = pd.DataFrame([wireless_input_data])
        
        # This returns a numpy array like [[1, 1, 0]]
        predictions_numeric = model.predict(input_df)
        
        # Map the numeric predictions back to human-readable strings
        predicted_features = [name for name, present in zip(output_labels, predictions_numeric[0]) if present]
        
        return predicted_features
    except KeyError as e:
        logging.error(f"Error during wireless prediction: Missing feature in input data - {e}")
        return ["An error occurred due to missing input."]
    except Exception as e:
        logging.error(f"Error during wireless prediction: {e}")
        return ["An error occurred."]