import numpy as np

def create_forecasting_sequences(data, look_back, forecast_horizon):
    """Create sequential data for forecasting."""
    X, y = [], []
    for i in range(len(data) - look_back - forecast_horizon):
        X.append(data[i:(i + look_back), :])  # Input: past 'look_back' days
        y.append(data[i + look_back + forecast_horizon - 1, 0])  # Output: forecasted value
    return np.array(X), np.array(y)

def preprocess_data(data, scaler, look_back, forecast_horizon):
    """Preprocess the input data by scaling and reshaping for LSTM."""
    # Convert input list to NumPy array
    data = np.array(data).reshape(-1, 1)
    
    # Scale the data using the saved scaler
    data_scaled = scaler.transform(data)
    
    # Create the input sequence based on the look-back period and forecast horizon
    X_input, _ = create_forecasting_sequences(data_scaled, look_back, forecast_horizon)
    
    # Reshape to 3D for LSTM input
    X_input = np.reshape(X_input, (X_input.shape[0], X_input.shape[1], 1))
    
    return X_input
