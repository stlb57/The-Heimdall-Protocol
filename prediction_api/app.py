from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np

app = Flask(__name__)
CORS(app)

model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    """Predicts the failure probability based on telemetry data."""
    try:
        data = request.get_json()
        
        # Ensure the data contains the required features
        if not all(key in data for key in ['heart_rate', 'oxygen_level', 'temperature']):
            return jsonify({"error": "Missing required telemetry data"}), 400

        features = [data['heart_rate'], data['oxygen_level'], data['temperature']]
        
        # IsolationForest uses decision_function, not predict_proba.
        # Scores are <= 0 for inliers (normal) and > 0 for outliers (anomalies).
        anomaly_score = model.decision_function([features])[0]
        
        # Convert the anomaly score to a 0-1 probability.
        # This is a simple sigmoid-like scaling. As score goes from negative to positive,
        # probability goes from near 0 to near 1.
        failure_probability = 1 / (1 + np.exp(-anomaly_score * 5)) # The multiplier '5' sharpens the curve

        return jsonify({'failure_probability': failure_probability})

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": "Could not process request"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
