import json
import time
from flask import Flask
import random
import threading

fault_injected = False
app = Flask(__name__)

@app.route('/inject_fault', methods=['POST'])
def inject_fault():
    global fault_injected
    fault_injected = True
    return "Fault injected", 200

def stream_telemetry():
    while True:
        metrics = {
            "heart_rate": random.randint(60, 100),
            "oxygen_level": round(random.uniform(10.0, 30.0) if fault_injected else random.uniform(95.0, 100.0), 2),
            "temperature": round(random.uniform(36.5, 37.5), 2),
            "timestamp": int(time.time())
        }
        print(json.dumps(metrics))
        time.sleep(2)

telemetry_thread = threading.Thread(target=stream_telemetry)
telemetry_thread.daemon = True
telemetry_thread.start()

app.run(host='0.0.0.0', port=5001)

