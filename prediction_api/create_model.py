import joblib
from sklearn.svm import OneClassSVM
import numpy as np

# This is the same robust set of "healthy" data.
healthy_data = [
    [75, 98.5, 37.0], [80, 99.0, 36.8], [72, 98.2, 37.1], [85, 98.8, 36.9],
    [78, 99.1, 37.0], [88, 98.9, 36.8], [70, 98.0, 37.2], [90, 99.5, 36.7],
    [76, 98.6, 37.1], [81, 99.2, 36.9], [73, 98.3, 37.0], [86, 98.7, 36.8],
    [79, 99.3, 37.1], [87, 98.8, 36.9], [71, 98.1, 37.2], [89, 99.4, 36.7],
    [68, 99.8, 36.6], [92, 99.6, 36.8], [77, 98.4, 37.0], [83, 99.0, 36.9]
]

# --- MODEL CHANGE ---
# We are now using a OneClassSVM model. It is more robust for this type of anomaly detection.
# 'nu' is an estimate of the proportion of outliers in the data (a small number is good).
# 'gamma' and 'kernel' are standard SVM parameters.
model = OneClassSVM(kernel='rbf', gamma='auto', nu=0.05)

# Train the model on what healthy data looks like.
model.fit(healthy_data)

# Save the trained model to a file.
joblib.dump(model, 'model.pkl')

print("A new SVM model (model.pkl) has been created successfully.")
