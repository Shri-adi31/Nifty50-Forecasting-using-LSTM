# app/routers/historical.py
from fastapi import APIRouter
from app.database import get_collection

router = APIRouter()

@router.get("/historical")
def get_historical_data(start: str, end: str):
    collection = get_collection("niftybees_historical")  # Replace with your actual collection
    query = {
        "timestamp": {
            "$gte": start,
            "$lte": end
        }
    }
    # Fetch all relevant fields
    historical_data = list(collection.find(query, {"_id": 0, "open": 1, "close": 1, "high": 1, "low": 1, "pe_ratio": 1, "volume": 1, "timestamp": 1}))
    return historical_data
