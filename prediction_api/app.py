import logging
import os
from typing import Dict, List, Any, Tuple, Union

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np

# --- NEW: Setup professional logging ---
# This will provide more detailed logs than the default print statements.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialization ---
app = Flask(__name__)
CORS(app)

# --- NEW: Load model with error handling ---
try:
    model = joblib.load('model.pkl')
    logging.info("Model 'model.pkl' loaded successfully.")
except FileNotFoundError:
    logging.error("Fatal: model.pkl not found. The application cannot start.")
    # In a real scenario, you might exit or have a fallback.
    model = None
except Exception as e:
    logging.error(f"An unexpected error occurred while loading the model: {e}")
    model = None


# --- Type hint for expected data structure ---
TelemetryData = Dict[str, Union[int, float]]


@app.route('/predict', methods=['POST'])
def predict() -> Tuple[Any, int]:
    """Predicts the failure probability based on telemetry data."""
    if not model:
        logging.error("Prediction failed because the model is not loaded.")
        return jsonify({"error": "Model not available"}), 503  # 503 Service Unavailable

    try:
        data: TelemetryData = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON or empty request body"}), 400

        required_keys = ['heart_rate', 'oxygen_level', 'temperature']
        if not all(key in data for key in required_keys):
            missing_keys = [key for key in required_keys if key not in data]
            # NEW: More descriptive error message
            error_msg = f"Missing required telemetry data: {', '.join(missing_keys)}"
            logging.warning(f"Bad request: {error_msg}")
            return jsonify({"error": error_msg}), 400

        features: List[Union[int, float]] = [data['heart_rate'], data['oxygen_level'], data['temperature']]
        
        # [cite_start]The core prediction logic remains UNCHANGED [cite: 1]
        anomaly_score: float = model.decision_function([features])[0]
        failure_probability: float = 1 / (1 + np.exp(-anomaly_score * 15))

        logging.info(f"Prediction successful for data: {data}. Result: {failure_probability:.4f}")
        return jsonify({'failure_probability': failure_probability}), 200

    except TypeError:
        # NEW: Specific error handling for non-numeric data
        logging.warning("Bad request: Telemetry data contained non-numeric values.")
        return jsonify({"error": "Invalid data type in request. All telemetry values must be numbers."}), 400
    except Exception as e:
        # NEW: Log the actual exception for better debugging
        logging.error(f"An unexpected error occurred during prediction: {e}", exc_info=True)
        return jsonify({"error": "Could not process request due to an internal server error."}), 500


if __name__ == '__main__':
    # --- NEW: Use environment variables for configuration ---
    # This allows you to change the host and port without editing the code.
    # Example: PORT=5003 python app.py
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5002))
    
    app.run(host=host, port=port)
