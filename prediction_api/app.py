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
            return jsonify({"error": "error_msg"}), 400

        features: List[Union[int, float]] = [data['heart_rate'], data['oxygen_level'], data['temperature']]
        
        anomaly_score: float = model.decision_function([features])[0]

        # --- THE FINAL, SIMPLIFIED FIX: DIRECT LINEAR SCALING ---
        # We are abandoning the sigmoid (exp) function because the model's capped score
        # is too small for it to work effectively.
        
        # This new logic is simple and aggressive:
        # 1. Take the absolute value of the score.
        # 2. Linearly scale it. We'll define a score of 0.2 or higher as 100% failure.
        # 3. Cap the result between 0.0 and 1.0 to ensure it's a valid probability.
        
        absolute_score = abs(anomaly_score)
        
        # We define our 'failure threshold' for the score. Let's say a score of 0.2 is max failure.
        FAILURE_SCORE_THRESHOLD = 0.2
        
        # Scale the score to a 0-1 range based on our threshold
        scaled_prob = absolute_score / FAILURE_SCORE_THRESHOLD
        
        # Clamp the value between 0 and 1 to handle scores above the threshold
        failure_probability = max(0.0, min(1.0, scaled_prob))

        logging.info(f"Prediction successful. Score: {anomaly_score:.4f}, Prob: {failure_probability:.4f}")
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
