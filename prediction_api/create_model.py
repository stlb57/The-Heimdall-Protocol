import joblib
from sklearn.ensemble import IsolationForest
import numpy as np

# This is sample "healthy" data for our astronaut.
# Each inner list represents [heart_rate, oxygen_level, temperature].
healthy_data = [
    [75, 98.5, 37.0],
    [80, 99.0, 36.8],
    [72, 98.2, 37.1],
    [85, 98.8, 36.9],
    [78, 99.1, 37.0],
    [88, 98.9, 36.8],
    [70, 98.0, 37.2],
    [90, 99.5, 36.7]
]

# We are using an "Isolation Forest" model. It's good at learning
# what "normal" looks like and then spotting data that deviates from it.
model = IsolationForest(contamination=0.1) # Assume about 10% of data could be anomalies

# Train the model on what healthy data looks like.
model.fit(healthy_data)

# Save the trained model to a file.
joblib.dump(model, 'model.pkl')

print("model.pkl has been created successfully.")
