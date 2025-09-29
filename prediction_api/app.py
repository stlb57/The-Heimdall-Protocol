from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import logging
import os
from typing import Dict, List, Any, Tuple, Union

# --- Setup professional logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialization ---
app = Flask(__name__)
CORS(app)

# --- Load model with error handling ---
try:
    model = joblib.load('model.pkl')
    logging.info("Model 'model.pkl' loaded successfully.")
except FileNotFoundError:
    logging.error("Fatal: model.pkl not found. The application cannot start.")
    model = None
except Exception as e:
    logging.error(f"An unexpected error occurred while loading the model: {e}")
    model = None

TelemetryData = Dict[str, Union[int, float]]

@app.route('/predict', methods=['POST'])
def predict() -> Tuple[Any, int]:
    """Predicts the failure probability based on telemetry data."""
    if not model:
        logging.error("Prediction failed because the model is not loaded.")
        return jsonify({"error": "Model not available"}), 503

    try:
        data: TelemetryData = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON or empty request body"}), 400

        required_keys = ['heart_rate', 'oxygen_level', 'temperature']
        if not all(key in data for key in required_keys):
            missing_keys = [key for key in required_keys if key not in data]
            error_msg = f"Missing required telemetry data: {', '.join(missing_keys)}"
            logging.warning(f"Bad request: {error_msg}")
            return jsonify({"error": error_msg}), 400

        features: List[Union[int, float]] = [data['heart_rate'], data['oxygen_level'], data['temperature']]
        
        # --- THE CORRECTED LOGIC ---
        # The model's 'predict' function returns -1 for an anomaly (outlier) and 1 for normal (inlier).
        
        prediction_result = model.predict([features])[0]
        
        if prediction_result == -1:
            # CORRECT: If the model flags it as an ANOMALY (-1), set probability to a very high number.
            failure_probability = 0.999
        else:
            # CORRECT: If the model considers it NORMAL (1), set probability to a very low number.
            failure_probability = 0.01

        logging.info(f"Prediction successful. Result: {prediction_result}, Prob: {failure_probability:.4f}")
        return jsonify({'failure_probability': failure_probability}), 200

    except TypeError:
        logging.warning("Bad request: Telemetry data contained non-numeric values.")
        return jsonify({"error": "Invalid data type in request. All telemetry values must be numbers."}), 400
    except Exception as e:
        logging.error(f"An unexpected error occurred during prediction: {e}", exc_info=True)
        return jsonify({"error": "Could not process request due to an internal server error."}), 500


if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5002))
    app.run(host=host, port=port)
