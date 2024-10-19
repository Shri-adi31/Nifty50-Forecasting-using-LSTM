# app/routers/forecast.py
from fastapi import APIRouter, HTTPException
from app.database import get_collection
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_url = os.getenv("FORECAST_API_URL", "http://127.0.0.1:8001")

router = APIRouter()

def fetch_latest_data(limit: int):
    """
    Fetch the latest `limit` records from MongoDB Atlas.
    """
    collection = get_collection("niftybees_historical")
    
    # Fetch the latest `limit` records sorted by timestamp in descending order
    latest_data = list(collection.find({}, {"_id": 0}).sort("_id", -1).limit(limit))
    
    # Reverse the data to maintain chronological order
    return latest_data[::-1]

@router.post("/forecast_1day")
def get_forecast_1day():
    data = fetch_latest_data(limit=60)

    fetchdata_21 = data[-21:]
    historical_data = data[-45:]

    # Extract 'close' values for forecasting
    data_list = [item['close'] for item in fetchdata_21]

    try:
        response = requests.post(
            f'{api_url}/predict_1days',
            json={"data": data_list}
        )
        response.raise_for_status()
        forecast_response = response.json()
        forecast_data = forecast_response.get('1_day_predictions', []) 
        print(forecast_data) 
    except requests.exceptions.RequestException as error:
        print("Error fetching forecast data:", error)
        raise HTTPException(status_code=500, detail="Forecast service error")

    return {
        "historical_data": historical_data,
        "forecast": forecast_data
    }

@router.post("/forecast_7day")
def get_forecast_7day():
    data = fetch_latest_data(limit=60)
    
    fetchdata_21 = data[-21:]
    historical_data = data[-45:]

    # Extract 'close' values for forecasting
    data_list = [item['close'] for item in fetchdata_21]

    try:
        response = requests.post(
            f'{api_url}/predict_7days',
            json={"data": data_list}
        )
        response.raise_for_status()
        forecast_response = response.json()
        forecast_data = forecast_response.get('7_day_predictions', []) 
        print(forecast_data)  # Uncomment this line if you need to debug the forecast data
    except requests.exceptions.RequestException as error:
        print("Error fetching forecast data:", error)
        raise HTTPException(status_code=500, detail="Forecast service error")

    return {
        "historical_data": historical_data,
        "forecast": forecast_data
    }
