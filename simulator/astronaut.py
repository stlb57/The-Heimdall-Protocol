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

# --- THE FIX: Re-introduce state for gradual degradation ---
# We use a simple dictionary to hold the current oxygen level.
SIMULATOR_STATE = {'oxygen_level': 99.9}

def get_vitals():
    """Simulates generating astronaut vitals with slow oxygen degradation."""
    global SIMULATOR_STATE
    
    fault_active = os.path.exists("/tmp/fault")

    if fault_active:
        # Extreme, catastrophic failure values
        heart_rate = random.randint(240, 280)
        oxygen_level = random.uniform(0, 10) # Critical oxygen
        temperature = round(random.uniform(43.0, 45.0), 2)
    else:
        # --- THE FIX: Normal operation now has degrading oxygen ---
        # This will create variable probabilities as oxygen slowly drops.
        heart_rate = random.randint(70, 85)
        # Decrease the oxygen level slightly with each call
        SIMULATOR_STATE['oxygen_level'] -= random.uniform(0.1, 0.4)
        if SIMULATOR_STATE['oxygen_level'] < 85: # Don't let it drop too low in normal state
            SIMULATOR_STATE['oxygen_level'] = 95.0
        oxygen_level = SIMULATOR_STATE['oxygen_level']
        temperature = round(random.uniform(36.6, 37.2), 2)

    telemetry_for_prediction = {
        "heart_rate": heart_rate,
        "oxygen_level": round(oxygen_level, 2),
        "temperature": temperature
    }
    return telemetry_for_prediction

@app.route('/telemetry', methods=['GET'])
def telemetry():
    """Provides the latest vitals as a JSON response."""
    current_vitals = get_vitals()
    print(json.dumps(current_vitals))
    return jsonify(current_vitals)

@app.route('/inject_fault', methods=['POST'])
def inject_fault():
    """Creates/deletes a fault file and resets the simulation state."""
    global SIMULATOR_STATE
    try:
        if not os.path.exists("/tmp/fault"):
            with open("/tmp/fault", "w") as f:
                f.write("fault activated")
            print("FAULT INJECTED VIA API CALL.")
            return "Fault injected successfully.", 200
        else:
            os.remove("/tmp/fault")
            # --- THE FIX: Reset oxygen level when fault is cleared ---
            SIMULATOR_STATE['oxygen_level'] = 99.9
            print("FAULT CLEARED & SIMULATOR RESET VIA API CALL.")
            return "Fault cleared and simulator reset.", 200
    except Exception as e:
        print(f"Error managing fault file: {e}")
        return "Error managing fault state.", 500

if __name__ == "__main__":
    if os.path.exists("/tmp/fault"):
        os.remove("/tmp/fault")
    print(f"🚀 Starting simulation API for Astronaut ID: {ASTRONAUT_ID}")
    app.run(host='0.0.0.0', port=5001)
