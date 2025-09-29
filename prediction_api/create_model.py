import joblib
from sklearn.ensemble import IsolationForest
import numpy as np

# This is a larger, more realistic set of "healthy" data for our astronaut.
# It includes more variance to give the model a better understanding of "normal".
healthy_data = [
    [75, 98.5, 37.0], [80, 99.0, 36.8], [72, 98.2, 37.1], [85, 98.8, 36.9],
    [78, 99.1, 37.0], [88, 98.9, 36.8], [70, 98.0, 37.2], [90, 99.5, 36.7],
    [76, 98.6, 37.1], [81, 99.2, 36.9], [73, 98.3, 37.0], [86, 98.7, 36.8],
    [79, 99.3, 37.1], [87, 98.8, 36.9], [71, 98.1, 37.2], [89, 99.4, 36.7],
    [68, 99.8, 36.6], [92, 99.6, 36.8], [77, 98.4, 37.0], [83, 99.0, 36.9]
]


# We are using an "Isolation Forest" model.
# Setting contamination to 'auto' is generally more robust than a fixed value.
model = IsolationForest(contamination='auto', random_state=42)

# Train the model on what healthy data looks like.
model.fit(healthy_data)

# Save the trained model to a file.
joblib.dump(model, 'model.pkl')

print("A new, more robust model.pkl has been created successfully.")
