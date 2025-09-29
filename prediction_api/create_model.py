import joblib
from sklearn.svm import OneClassSVM
import numpy as np

print("Generating a more robust training dataset...")

# --- NEW: Generate a larger, more realistic dataset ---
# Instead of a small, fixed list, we'll generate 500 "healthy" samples.
# This makes the model much more aware of the normal operating range.
np.random.seed(42) # for reproducibility
num_samples = 500

heart_rates = np.random.uniform(70, 90, num_samples)
oxygen_levels = np.random.uniform(98.0, 99.5, num_samples)
temperatures = np.random.uniform(36.7, 37.2, num_samples)

# Combine into a single dataset
healthy_data = np.column_stack([heart_rates, oxygen_levels, temperatures])

print(f"{num_samples} healthy data points generated.")

# --- MODEL TRAINING (same as before, but on the new data) ---
# 'nu' is an estimate of the proportion of outliers in the data. 
# 0.05 means we expect about 5% of the training data to be noisy.
model = OneClassSVM(kernel='rbf', gamma='auto', nu=0.05)

# Train the model on what healthy data looks like.
print("Training the new OneClassSVM model...")
model.fit(healthy_data)

# Save the trained model to a file.
joblib.dump(model, 'model.pkl')

print("\n✅ A new, more robust model (model.pkl) has been created successfully.")
print("   You can now rebuild and deploy your application.")
