import json
import yfinance as yf
import pandas as pd
from pymongo import MongoClient, errors,DESCENDING
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
TICKER = 'NIFTYBEES.NS'  # Yahoo Finance ticker for NiftyBEES ETF
JSON_OUTPUT_FILE = 'niftybees_data.json'

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI')
DATABASE_NAME = 'finance_app'
COLLECTION_NAME = 'niftybees_historical'

# Establish MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    print("Connected to MongoDB successfully.")
except errors.ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")

def get_last_inserted_date():
    """Fetch the latest timestamp from MongoDB collection."""
    try:
        last_record = collection.find_one(sort=[('_id', DESCENDING)])
        if last_record:
            last_timestamp = last_record["timestamp"]
            print(f"Last inserted data was on: {last_timestamp}")
            return last_timestamp
        else:
            print("No previous data found, using default start date.")
            return None  # No data in the collection
    except Exception as e:
        print(f"Error fetching last inserted date: {e}")
        return None

def fetch_data(ticker, start, end):
    """Fetch historical data from Yahoo Finance."""
    try:
        print(f"Fetching data for {ticker} from {start} to {end}")
        data = yf.download(ticker, start=start, end=end, progress=False)
        if data.empty:
            print("No data fetched.")
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        print(f"Error fetching data from Yahoo Finance: {e}")
        return pd.DataFrame()

def fetch_additional_info(ticker):
    """Fetch additional information like P/E ratio from Yahoo Finance."""
    try:
        print(f"Fetching additional info for {ticker}")
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Collect P/E ratio
        pe_ratio = info.get("trailingPE", None)
        return pe_ratio
    except Exception as e:
        print(f"Error fetching additional info: {e}")
        return None

def clean_transform_data(df, pe_ratio):
    """Clean and transform data to match the desired MongoDB schema."""
    df.rename(columns={
        'Date': 'timestamp',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Adj Close': 'adj_close',
        'Volume': 'volume'
    }, inplace=True)

    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date
    df['pe_ratio'] = pe_ratio
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'pe_ratio']]

    return df

def save_data_as_json(data, filename=JSON_OUTPUT_FILE):
    """Save DataFrame to a JSON file."""
    records = data.to_dict(orient='records')

    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.extend(records)
    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=4, default=str)

    print(f"Data saved to {filename}")

def insert_json_into_mongodb(json_file):
    """Insert data from JSON file into MongoDB Atlas."""
    try:
        print(f"Inserting data from {json_file} into MongoDB")
        with open(json_file, 'r') as file:
            records = json.load(file)
        for record in records:
            collection.update_one(
                {"timestamp": record["timestamp"]},
                {"$set": record},
                upsert=True
            )
        print("Data insertion complete")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

def collect_data():
    """Main function to fetch, process, and store data."""
    last_inserted_date = get_last_inserted_date()

    if last_inserted_date:
        start_date = (last_inserted_date)
    else:
        start_date = '2014-05-26'

    end_date = datetime.today().strftime('%Y-%m-%d')

    raw_data = fetch_data(TICKER, start_date, end_date)
    if raw_data.empty:
        return {"message": "No new data to insert."}

    pe_ratio = fetch_additional_info(TICKER)
    clean_data = clean_transform_data(raw_data, pe_ratio)
    save_data_as_json(clean_data)
    insert_json_into_mongodb(JSON_OUTPUT_FILE)

    return {"message": f"Data from {start_date} to {end_date} collected and stored successfully."}

if __name__ == "__main__":
    result = collect_data()
    print(result)
