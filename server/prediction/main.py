from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prediction.model_operation import load_scaler
from prediction.preprocessing import preprocess_data
from prediction.model_operation import load_model_safe

import os

# Initialize FastAPI app
app = FastAPI()

# Define the paths to the model files relative to the application's root directory
model_1day_path = 'prediction/model/saved_model1day.h5'

try:
    model_1day = load_model_safe(model_1day_path)
except FileNotFoundError as e:
    print(e)
    raise HTTPException(status_code=500, detail=str(e))

# Load the scaler
scaler = load_scaler('prediction/model/scaler.pkl')

# Define input structure using Pydantic
class StockData(BaseModel):
    data: list

# POST endpoint for 7-day forecast
@app.post("/predict_7days")
async def predict_7days(stock_data: StockData):
    data = stock_data.data
    
    prediction_list = []
    for i in range (7):
            # Ensure data is provided
            if len(data) < 21:
                raise HTTPException(status_code=400, detail="Not enough data. Need at least 21 values.")
            
            # Preprocess the data with a 21-day look-back period for a 7-days forecast
            X_input = preprocess_data(data, scaler,look_back=21)
            
            # Make prediction using the 7-day model
            predictions = model_1day(X_input)
            
            # Inverse scale the prediction back to the original scale
            predictions_rescaled = scaler.inverse_transform(predictions)
            
            prediction_list.append(predictions_rescaled.flatten().tolist())

            data.extend(predictions_rescaled.flatten().tolist())
            data = data[1:]
    # Return the forecasted stock prices as a list
    return {"7_day_predictions": prediction_list}

# POST endpoint for 1-day forecast
@app.post("/predict_1days")
async def predict_1days(stock_data: StockData):
    data = stock_data.data
    
    # Ensure data is provided
    if len(data) < 21:
        raise HTTPException(status_code=400, detail="Not enough data. Need at least 21 values.")
    
    
    # Preprocess the data with a 21-day look-back period for a 2-day forecast
    X_input = preprocess_data(data, scaler, look_back=21)
    
    # Make prediction using the 2-day model
    predictions = model_1day(X_input)
    
    # Inverse scale the prediction back to the original scale
    predictions_rescaled = scaler.inverse_transform(predictions)
    
    # Return the forecasted stock prices as a list
    return {"1_day_predictions": predictions_rescaled.tolist()}
