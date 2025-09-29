import time
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
CORS(app)

# --- State ---
# This global variable will control the simulator's state
STATE = {"fault_injected": False}

def get_healthy_telemetry():
    """Generates a reading of healthy vital signs."""
    return {
        "heart_rate": random.uniform(70, 90),
        "oxygen_level": random.uniform(98.0, 99.5),
        "temperature": random.uniform(36.7, 37.2)
    }

def get_anomalous_telemetry():
    """Generates a reading of dangerous vital signs."""
    return {
        "heart_rate": random.uniform(130, 160),
        "oxygen_level": random.uniform(85.0, 92.0),
        "temperature": random.uniform(38.0, 40.0)
    }

# --- API Endpoints ---

@app.route('/telemetry', methods=['GET'])
def get_telemetry():
    """Provides the current telemetry data based on the system state."""
    if STATE["fault_injected"]:
        logging.warning("System fault is active. Generating anomalous data.")
        telemetry = get_anomalous_telemetry()
    else:
        logging.info("System is nominal. Generating healthy data.")
        telemetry = get_healthy_telemetry()
    return jsonify(telemetry)

@app.route('/inject_fault', methods=['POST'])
def inject_fault():
    """Injects a fault into the system."""
    logging.critical("FAULT INJECTION ACTIVATED!")
    STATE["fault_injected"] = True
    return jsonify({"status": "success", "message": "Fault injected. System is now generating anomalous data."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
