from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prediction.model_operation import load_scaler
from prediction.preprocessing import preprocess_data
from prediction.model_operation import load_model_safe

import os

# Initialize FastAPI app
app = FastAPI()

# Define the paths to the model files relative to the application's root directory
model_7day_path = 'prediction/model/models_7day.h5'
model_2day_path = 'prediction/model/models_1day.h5'

try:
    model_7day = load_model_safe(model_7day_path)
    model_2day = load_model_safe(model_2day_path)
except FileNotFoundError as e:
    print(e)
    raise HTTPException(status_code=500, detail=str(e))

# Load the scaler
scaler = load_scaler('prediction/model/scaler.pkl')

# Define input structure using Pydantic
class StockData(BaseModel):
    data: list

# POST endpoint for 7-day forecast
@app.post("/predict_7days/")
async def predict_7days(stock_data: StockData):
    data = stock_data.data
    
    # Ensure data is provided
    if len(data) < 60:
        raise HTTPException(status_code=400, detail="Not enough data. Need at least 60 values.")
    
    # Preprocess the data with a 60-day look-back period for a 7-day forecast
    X_input = preprocess_data(data, scaler, look_back=60, forecast_horizon=7)
    
    # Make prediction using the 7-day model
    predictions = model_7day(X_input)
    
    # Inverse scale the prediction back to the original scale
    predictions_rescaled = scaler.inverse_transform(predictions)
    
    # Return the forecasted stock prices as a list
    return {"7_day_predictions": predictions_rescaled.tolist()}

# POST endpoint for 2-day forecast
@app.post("/predict_2days/")
async def predict_2days(stock_data: StockData):
    data = stock_data.data
    
    # Ensure data is provided
    if len(data) < 21:
        raise HTTPException(status_code=400, detail="Not enough data. Need at least 21 values.")
    
    # Preprocess the data with a 21-day look-back period for a 2-day forecast
    X_input = preprocess_data(data, scaler, look_back=21, forecast_horizon=2)
    
    # Make prediction using the 2-day model
    predictions = model_2day(X_input)
    
    # Inverse scale the prediction back to the original scale
    predictions_rescaled = scaler.inverse_transform(predictions)
    
    # Return the forecasted stock prices as a list
    return {"2_day_predictions": predictions_rescaled.tolist()}
