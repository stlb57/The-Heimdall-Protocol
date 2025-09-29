# heimdall-protocol/simulator/astronaut.py

import time
import random
import json
import uuid
import os

ASTRONAUT_ID = str(uuid.uuid4())[:8]
oxygen_level = 99.9
start_time = time.time()
fault_injected = False

def get_vitals():
    """Simulates generating fluctuating astronaut vitals."""
    global oxygen_level, start_time, fault_injected
    
    # Check if a fault has been injected by looking for a specific file
    if not fault_injected and os.path.exists("/tmp/fault"):
        print("FAULT DETECTED VIA FILE. SIMULATING ANOMALY.")
        fault_injected = True

    # Generate anomalous data if fault is active
    if fault_injected:
        heart_rate = random.randint(120, 160)
        oxygen_level -= random.uniform(5, 10) # Rapid oxygen loss
        temperature = round(random.uniform(38.0, 39.5), 2)
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

if __name__ == "__main__":
    print(f"🚀 Starting simulation for Astronaut ID: {ASTRONAUT_ID}")
    try:
        while True:
            current_vitals = get_vitals()
            print(json.dumps(current_vitals))
            
            if oxygen_level <= 0:
                print(f"🚨 CRITICAL: Oxygen depleted for {ASTRONAUT_ID}.")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print(f"🛑 Simulation stopped for {ASTRONAUT_ID}.")
