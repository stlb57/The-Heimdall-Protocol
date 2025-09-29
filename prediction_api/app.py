from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)
model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = [data['heart_rate'], data['oxygen_level'], data['temperature']]
    failure_probability = model.predict_proba([features])[0][1]
    return jsonify({'failure_probability': failure_probability})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

