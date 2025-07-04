# app/routes.py

from flask import render_template, request, Blueprint
from app.services import (
    load_and_process_data, 
    get_recommendations, 
    load_ml_artifacts,  # Updated function name
    predict_processor_function,
    predict_wireless_features # New function
)
from config import Config
import pandas as pd

main = Blueprint('main', __name__)

# --- GLOBAL DATA AND MODEL LOADING ---
df_processed = load_and_process_data(Config.DATA_FILE_PATH)

# Load all ML artifacts once when the application starts
function_model, function_label_encoder, wireless_model = load_ml_artifacts(
    Config.FUNCTION_CLASSIFIER_PATH, 
    Config.LABEL_ENCODER_PATH,
    Config.WIRELESS_PREDICTOR_PATH
)

# --- HELPER FUNCTIONS ---
def _build_prediction_input_from_form(form):
    """
    Safely builds the model input dictionary from form data,
    providing defaults for features not in the form.
    """
    # Default values for features the model needs but are not in the form
    defaults = {
        'GPU Clock': 800,
        'Total L2 Cache': 4096,
        'Total L3 Cache': 8192,
        'bluetooth_version': 5.2,
        'Semiconductor Technology': 'FinFET',
        'Fab': 'TSMC',
        'has_wifi_6_or_higher': True,
        'has_nfc': True,
        'has_efficiency_cores': True
    }
    
    # Extract and convert required form data
    input_data = {
        'Designer': form.get('designer'),
        'Year Released': int(form.get('year_released', 0)),
        'Number of processor core(s)': int(form.get('num_cores', 0)),
        'Feature Size': float(form.get('feature_size', 0.0)),
        'has_performance_cores': form.get('has_performance_cores') == '1',
        'has_5g': form.get('has_5g') == '1',
    }
    
    # Combine form data with defaults, letting form data take precedence
    return {**defaults, **input_data}

# --- WEB ROUTES ---
@main.route('/', methods=['GET', 'POST'])
def index():
    # ... (This route remains unchanged) ...
    if request.method == 'POST':
        requirements = { 'designer': request.form.get('designer'), 'needs_5g': request.form.get('needs_5g') == 'true', 'needs_wifi_6': request.form.get('needs_wifi_6') == 'true' }
        try:
            if request.form.get('min_year') and request.form.get('max_year'):
                requirements['min_year'] = int(request.form.get('min_year'))
                requirements['max_year'] = int(request.form.get('max_year'))
            if request.form.get('min_cores') and request.form.get('max_cores'):
                requirements['min_cores'] = int(request.form.get('min_cores'))
                requirements['max_cores'] = int(request.form.get('max_cores'))
        except (ValueError, TypeError): pass
        recommendations_df = get_recommendations(requirements, df_processed)
        recommendations_list = recommendations_df.to_dict('records')
        return render_template('results.html', recommendations=recommendations_list)
    return render_template('index.html')


@main.route('/predict', methods=['GET', 'POST'])
def predict():
    """Handles the ML-powered processor analyzer page."""
    function_prediction = None
    wireless_prediction = None
    
    if request.method == 'POST':
        # Models are loaded at startup. If they failed, the app wouldn't start.
        # A check here is fine, but a more robust app might have a health check endpoint.
        if not (function_model and wireless_model):
            return "Error: Models are not available.", 500
        
        try:
            input_data = _build_prediction_input_from_form(request.form)
            
            # Get prediction from the function model
            function_prediction = predict_processor_function(
                function_model, function_label_encoder, input_data
            )
            
            # Get prediction from the wireless features model
            wireless_prediction = predict_wireless_features(
                wireless_model, input_data
            )
        except (ValueError, TypeError) as e:
            # Handle specific errors related to form input conversion
            print(f"Error processing form input: {e}")
            function_prediction = "Error: Invalid input provided. Please check your values."
        except Exception as e:
            # A catch-all for other unexpected errors
            print(f"An unexpected error occurred during prediction: {e}")
            function_prediction = "Error: Could not make a prediction due to a server error."

    # Render the page, passing both prediction results to the template
    return render_template('predict.html', 
                           function_prediction=function_prediction,
                           wireless_prediction=wireless_prediction)