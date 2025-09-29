from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import logging
import os
from typing import Dict, List, Any, Tuple, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
CORS(app)

try:
    model = joblib.load('model.pkl')
    logging.info("Model 'model.pkl' loaded successfully.")
except Exception as e:
    logging.error(f"Fatal error loading model.pkl: {e}")
    model = None

TelemetryData = Dict[str, Union[int, float]]

@app.route('/predict', methods=['POST'])
def predict() -> Tuple[Any, int]:
    """Predicts the failure probability based on telemetry data."""
    if not model:
        return jsonify({"error": "Model not available"}), 503

    try:
        data: TelemetryData = request.get_json()
        if not all(key in data for key in ['heart_rate', 'oxygen_level', 'temperature']):
            return jsonify({"error": "Missing required telemetry data"}), 400

        features: List[Union[int, float]] = [data['heart_rate'], data['oxygen_level'], data['temperature']]
        
        # --- THE FIX: Return to the nuanced decision_function score ---
        anomaly_score: float = model.decision_function([features])[0]

        # --- THE FIX: Use direct linear scaling for dynamic probabilities ---
        # This logic converts the model's raw score into our desired variable output.
        absolute_score = abs(anomaly_score)
        
        # We define a score of 0.3 as the point of 100% failure.
        # This value is tuned to give variability below the 95% threshold for normal degradation,
        # but ensure the extreme fault values push it over 95%.
        FAILURE_SCORE_THRESHOLD = 0.3
        
        scaled_prob = absolute_score / FAILURE_SCORE_THRESHOLD
        
        failure_probability = max(0.0, min(1.0, scaled_prob))

        logging.info(f"Prediction successful. Score: {anomaly_score:.4f}, Prob: {failure_probability:.4f}")
        return jsonify({'failure_probability': failure_probability}), 200

    except Exception as e:
        logging.error(f"An unexpected error occurred during prediction: {e}", exc_info=True)
        return jsonify({"error": "Could not process request due to an internal server error."}), 500

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5002))
    app.run(host=host, port=port)
