from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)
model = joblib.load('model.pkl')

def sigmoid(x):
    # Maps any real value to a value between 0 and 1
    return 1 / (1 + np.exp(-x))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = [data['heart_rate'], data['oxygen_level'], data['temperature']]
    
    # Use decision_function() which returns an anomaly score.
    # Lower scores mean more anomalous.
    anomaly_score = model.decision_function([features])[0]
    
    # We negate the score and apply a sigmoid function.
    # This maps a highly anomalous (very negative) score to a probability near 1.0.
    failure_probability = sigmoid(-anomaly_score)
    
    return jsonify({'failure_probability': failure_probability})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
