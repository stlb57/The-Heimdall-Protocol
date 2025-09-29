# heimdall-protocol/simulator/astronaut.py

import time
import random
import json
import uuid
import os
from flask import Flask, jsonify
from flask_cors import CORS

# --- NEW: Setup Flask App ---
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for the web UI

# --- SIMULATOR STATE (Moved to global scope) ---
ASTRONAUT_ID = str(uuid.uuid4())[:8]
oxygen_level = 99.9
fault_injected = False

def get_vitals():
    """Simulates generating fluctuating astronaut vitals."""
    global oxygen_level, fault_injected
    
    # Check if a fault has been injected by looking for a specific file
    if not fault_injected and os.path.exists("/tmp/fault"):
        print("FAULT DETECTED VIA FILE. SIMULATING ANOMALY.")
        fault_injected = True

    # Generate anomalous data if fault is active
    if fault_injected:
        # --- NEW, EVEN MORE EXTREME VALUES ---
        # These values are pushed to a point of catastrophic system failure.
        
        heart_rate = random.randint(240, 280)           # Represents ventricular fibrillation/tachycardia
        
        # Instead of a rapid decrease, we'll set oxygen to a critically low level instantly.
        oxygen_level = random.uniform(0, 10)
        
        temperature = round(random.uniform(43.0, 45.0), 2)  # Represents complete thermoregulatory failure
    else:
        heart_rate = random.randint(65, 85)
        oxygen_level -= random.uniform(0.05, 0.2)
        temperature = round(random.uniform(36.5, 37.2), 2)
        
    if oxygen_level < 0:
        oxygen_level = 0
    
    # This is the JSON object that will be sent to the prediction API
    # It must contain the keys the model was trained on.
    telemetry_for_prediction = {
        "heart_rate": heart_rate,
        "oxygen_level": round(oxygen_level, 2),
        "temperature": temperature
    }
    return telemetry_for_prediction

# --- NEW: API Endpoint for Telemetry ---
@app.route('/telemetry', methods=['GET'])
def telemetry():
    """Provides the latest vitals as a JSON response."""
    current_vitals = get_vitals()
    # Also print to log so the Jenkins monitor stage still works
    print(json.dumps(current_vitals)) 
    return jsonify(current_vitals)

# --- NEW: API Endpoint for Injecting Fault ---
@app.route('/inject_fault', methods=['POST'])
def inject_fault():
    """Creates a file to trigger the fault condition."""
    global fault_injected
    if not fault_injected:
        # Create a file that get_vitals() will detect
        with open("/tmp/fault", "w") as f:
            f.write("fault activated")
        print("FAULT INJECTED VIA API CALL.")
        return "Fault injected successfully.", 200
    return "Fault has already been injected.", 400

# --- MODIFIED: Main execution block to run the web server ---
if __name__ == "__main__":
    print(f"🚀 Starting simulation API for Astronaut ID: {ASTRONAUT_ID}")
    # Run the Flask app on port 5001, accessible from outside the container
    app.run(host='0.0.0.0', port=5001)
