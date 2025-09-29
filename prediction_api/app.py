from flask import Flask, request, jsonify
import joblib
import numpy as np
app = Flask(__name__)
model = joblib.load('model.pkl')
def normalize_score(score):
    """
    Normalizes the Isolation Forest score to a 0-1 probability range.
    Scores are typically <= 0, where values closer to -0.5 are more anomalous.
    This is a simple sigmoid-like transformation.
    """
    return 1 / (1 + np.exp(score * 5)) 
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = [data['heart_rate'], data['oxygen_level'], data['temperature']]
        anomaly_score = model.decision_function([features])[0]
        failure_probability = normalize_score(anomaly_score)

        return jsonify({'failure_probability': failure_probability})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to process prediction request.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
