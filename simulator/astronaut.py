import time
import random
import json
import uuid
import os
from flask import Flask, jsonify
from flask_cors import CORS

# --- Initialization ---
app = Flask(__name__)
CORS(app)
ASTRONAUT_ID = str(uuid.uuid4())[:8]

# --- THE FIX: We will now manage the fault state within Flask's app context ---
# This ensures it's handled correctly for each web request.

def get_vitals():
    """
    Simulates generating astronaut vitals.
    This function is now STATELESS for normal operation.
    """
    # Check if a fault has been injected by looking for a specific file.
    fault_active = os.path.exists("/tmp/fault")

    # Generate anomalous data if fault is active
    if fault_active:
        # Extreme, catastrophic failure values
        heart_rate = random.randint(240, 280)
        oxygen_level = random.uniform(0, 10)
        temperature = round(random.uniform(43.0, 45.0), 2)
    else:
        # --- THE FIX: Always return a PERFECTLY HEALTHY reading for normal state ---
        # This prevents the slow degradation that caused the constant 99.9% probability.
        heart_rate = random.randint(70, 85)
        oxygen_level = random.uniform(98.0, 99.5)
        temperature = round(random.uniform(36.6, 37.2), 2)

    telemetry_for_prediction = {
        "heart_rate": heart_rate,
        "oxygen_level": round(oxygen_level, 2),
        "temperature": temperature
    }
    return telemetry_for_prediction

# --- API Endpoint for Telemetry ---
@app.route('/telemetry', methods=['GET'])
def telemetry():
    """Provides the latest vitals as a JSON response."""
    current_vitals = get_vitals()
    # Print to log so the Jenkins monitor stage still works
    print(json.dumps(current_vitals))
    return jsonify(current_vitals)

# --- API Endpoint for Injecting Fault ---
@app.route('/inject_fault', methods=['POST'])
def inject_fault():
    """Creates a file to trigger the fault condition."""
    try:
        # --- THE FIX: We remove the check that prevents re-injection ---
        # This allows you to trigger the fault even if the system is already in a fault state.
        # It also now includes logic to clear the fault.
        if not os.path.exists("/tmp/fault"):
            with open("/tmp/fault", "w") as f:
                f.write("fault activated")
            print("FAULT INJECTED VIA API CALL.")
            return "Fault injected successfully.", 200
        else:
            # If fault is already injected, this call will now clear it.
            os.remove("/tmp/fault")
            print("FAULT CLEARED VIA API CALL.")
            return "Fault cleared successfully.", 200
    except Exception as e:
        print(f"Error managing fault file: {e}")
        return "Error managing fault state.", 500

# --- Main execution block to run the web server ---
if __name__ == "__main__":
    # Clear any old fault files on startup
    if os.path.exists("/tmp/fault"):
        os.remove("/tmp/fault")
    print(f"🚀 Starting simulation API for Astronaut ID: {ASTRONAUT_ID}")
    app.run(host='0.0.0.0', port=5001)
