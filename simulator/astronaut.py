import json
import time
from flask import Flask, jsonify # Import jsonify
import random
import threading

# --- State Variables ---
fault_injected = False
# A global variable to hold the latest telemetry data
latest_metrics = {}
# A lock to prevent race conditions when accessing latest_metrics
data_lock = threading.Lock()

app = Flask(__name__)

# --- API Endpoints ---
@app.route('/inject_fault', methods=['POST'])
def inject_fault():
    """Sets a flag to start generating anomalous data."""
    global fault_injected
    fault_injected = True
    print("FAULT INJECTED")
    return "Fault injected successfully", 200

@app.route('/telemetry', methods=['GET'])
def get_telemetry():
    """Provides the latest telemetry data to the frontend."""
    with data_lock:
        return jsonify(latest_metrics)

# --- Background Telemetry Generation ---
def stream_telemetry():
    """Continuously generates and updates telemetry data in the background."""
    global latest_metrics
    while True:
        # Generate metrics
        metrics = {
            "heart_rate": random.randint(65, 85) if not fault_injected else random.randint(120, 160),
            "oxygen_level": round(random.uniform(96.0, 99.5), 2) if not fault_injected else round(random.uniform(80.0, 90.0), 2),
            "temperature": round(random.uniform(36.5, 37.2), 2) if not fault_injected else round(random.uniform(38.0, 39.5), 2),
            "timestamp": int(time.time())
        }
        
        # Update the global state safely
        with data_lock:
            latest_metrics = metrics
            
        # Also print for logging purposes (used by Jenkins)
        print(json.dumps(metrics))
        
        time.sleep(2) # Generate new data every 2 seconds

if __name__ == '__main__':
    # Start the background thread
    telemetry_thread = threading.Thread(target=stream_telemetry)
    telemetry_thread.daemon = True
    telemetry_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001)
