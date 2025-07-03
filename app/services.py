import pandas as pd
import re
import joblib

def load_and_process_data(file_path):
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

        columns_to_clean = ['Number of processor core(s)', 'Feature Size']
        for col in columns_to_clean:
            if col in df_raw.columns:
                df_raw[col] = clean_numeric_column(df_raw[col])
        
        df_processed = create_connectivity_features(df_raw)
        print("Dataset loaded and preprocessed successfully.")
        return df_processed
    except FileNotFoundError:
        print(f"ERROR: Data file not found at {file_path}.")
        return pd.DataFrame()

def get_recommendations(requirements, data):
    """Filters the dataset based on user requirements."""
    if data.empty: return pd.DataFrame()
    
    filtered_df = data.copy()
    if requirements.get('designer'):
        filtered_df = filtered_df[filtered_df['Designer'].str.lower() == requirements['designer'].lower()]
    if requirements.get('min_year') and requirements.get('max_year'):
        filtered_df = filtered_df[filtered_df['Year Released'].between(requirements['min_year'], requirements['max_year'])]
    if requirements.get('min_cores') and requirements.get('max_cores'):
        filtered_df = filtered_df[filtered_df['Number of processor core(s)'].between(requirements['min_cores'], requirements['max_cores'])]
    if requirements.get('needs_5g'):
        filtered_df = filtered_df[filtered_df['has_5g'] == True]
    if requirements.get('needs_wifi_6'):
        filtered_df = filtered_df[filtered_df['has_wifi_6_or_higher'] == True]
    
    display_columns = ['Designer', 'Serie', 'Type', 'Year Released', 'Number of processor core(s)', 'Feature Size', 'Function']
    display_columns = [col for col in display_columns if col in filtered_df.columns]
    
    return filtered_df[display_columns].sort_values(by='Year Released', ascending=False)


def load_ml_artifacts(function_model_path, encoder_path, wireless_model_path):
    """Loads all trained models and encoders from disk."""
    try:
        function_model = joblib.load(function_model_path)
        label_encoder = joblib.load(encoder_path)
        wireless_model = joblib.load(wireless_model_path)
        print("All ML artifacts loaded successfully.")
        return function_model, label_encoder, wireless_model
    except FileNotFoundError as e:
        print(f"ERROR: Could not load ML artifact. {e}")
        return None, None, None

def predict_processor_function(model, label_encoder, input_data):
    """Predicts the function of a processor."""
    if model is None or label_encoder is None: return "Error: Model not loaded."
    try:
        input_df = pd.DataFrame([input_data])
        prediction_numeric = model.predict(input_df)
        prediction_string = label_encoder.inverse_transform(prediction_numeric)
        return prediction_string[0]
    except Exception as e:
        print(f"Error during function prediction: {e}")
        return "An error occurred."

def predict_wireless_features(model, input_data):
    """Predicts the wireless features of a processor."""
    if model is None: return []
    try:
        # The wireless model was trained on a different feature set
        # We need to ensure the input DataFrame only contains those features
        wireless_features_columns = [
            'Year Released', 'Number of processor core(s)', 'Feature Size', 'GPU Clock',
            'Total L2 Cache', 'Total L3 Cache', 'Designer', 'Semiconductor Technology', 'Fab',
            'has_performance_cores', 'has_efficiency_cores'
        ]
        
        # Create a new dictionary with only the required columns
        wireless_input_data = {key: input_data[key] for key in wireless_features_columns}
        input_df = pd.DataFrame([wireless_input_data])
        
        # This returns a numpy array like [[1, 1, 0]]
        predictions_numeric = model.predict(input_df)
        
        # Map the numeric predictions back to human-readable strings
        feature_names = ['5G Support', 'Wi-Fi 6 or higher', 'USB 3.0 or higher']
        predicted_features = [name for name, present in zip(feature_names, predictions_numeric[0]) if present]
        
        return predicted_features
    except Exception as e:
        print(f"Error during wireless prediction: {e}")
        return ["An error occurred."]