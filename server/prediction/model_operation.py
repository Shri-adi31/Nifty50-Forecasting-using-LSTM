import tensorflow as tf
import joblib
import os

# Function to load model with error handling
def load_model_safe(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    return tf.keras.models.load_model(path)

def load_scaler(scaler_path):
    """Load the scaler using joblib."""
    return joblib.load(scaler_path)
