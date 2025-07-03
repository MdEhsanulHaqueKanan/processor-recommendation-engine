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
        if function_model and wireless_model:
            try:
                # Create the full input dictionary from form data
                input_data = {
                    'Year Released': int(request.form['Year Released']),
                    'Number of processor core(s)': int(request.form['Number of processor core(s)']),
                    'Feature Size': float(request.form['Feature Size']),
                    'Designer': request.form['Designer'],
                    'has_5g': 'has_5g' in request.form,
                    'has_performance_cores': 'has_performance_cores' in request.form,
                    'GPU Clock': 800, 'Total L2 Cache': 4096, 'Total L3 Cache': 8192,
                    'bluetooth_version': 5.2, 'Semiconductor Technology': 'FinFET', 'Fab': 'TSMC',
                    'has_wifi_6_or_higher': True, 'has_nfc': True, 'has_efficiency_cores': True
                }
                
                # Get prediction from the first model
                function_prediction = predict_processor_function(function_model, function_label_encoder, input_data)
                
                # Get prediction from the second model
                wireless_prediction = predict_wireless_features(wireless_model, input_data)

            except Exception as e:
                print(f"Error during prediction: {e}")
                function_prediction = "Error: Could not make a prediction. Please check your inputs."

    # Render the page, passing both prediction results to the template
    return render_template('predict.html', 
                           function_prediction=function_prediction,
                           wireless_prediction=wireless_prediction)