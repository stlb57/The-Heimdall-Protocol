from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)
model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = [data['heart_rate'], data['oxygen_level'], data['temperature']]

    # IsolationForest gives an anomaly score. Lower scores are more anomalous.
    # We get the opposite of the score, so negative values are anomalies.
    anomaly_score = model.score_samples([features])[0]

    # We can convert this score to a probability-like value between 0 and 1.
    # A simple sigmoid function works well here. As the score becomes more
    # negative (more anomalous), the probability approaches 1.
    failure_probability = 1.0 / (1.0 + np.exp(anomaly_score))

    return jsonify({'failure_probability': failure_probability})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
