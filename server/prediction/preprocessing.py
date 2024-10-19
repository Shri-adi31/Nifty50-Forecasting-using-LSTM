import numpy as np


def preprocess_data(data, scaler, look_back):
    """Preprocess the input data by scaling and reshaping for LSTM."""
    # Convert input list to NumPy array
    data = np.array(data).reshape(-1, 1)
    
    # Scale the data using the saved scaler
    data_scaled = scaler.transform(data)
  
    # Reshape to 3D for LSTM input
    X_input = np.reshape(data_scaled, ((1, look_back, 1)))
    
    return X_input
