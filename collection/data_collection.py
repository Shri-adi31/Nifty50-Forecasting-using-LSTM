import yfinance as yf
import pandas as pd
from pymongo import MongoClient
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
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def get_last_inserted_date():
    """Fetch the latest timestamp from MongoDB collection."""
    last_record = collection.find_one({}, sort=[("timestamp", -1)])
    if last_record:
        last_timestamp = last_record["timestamp"]
        print(f"Last inserted data was on: {last_timestamp}")
        return last_timestamp
    else:
        print("No previous data found, using default start date.")
        return None  # No data in the collection

def fetch_data(ticker, start, end):
    """Fetch historical data from Yahoo Finance."""
    print(f"Fetching data for {ticker} from {start} to {end}")
    data = yf.download(ticker, start=start, end=end, progress=False)
    data.reset_index(inplace=True)
    return data

def fetch_additional_info(ticker):
    """Fetch additional information like P/E ratio from Yahoo Finance."""
    print(f"Fetching additional info for {ticker}")
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Collect P/E ratio
    pe_ratio = info.get("trailingPE", None)
    
    return pe_ratio

def clean_transform_data(df, pe_ratio):
    """Clean and transform data to match the desired MongoDB schema."""
    # Rename columns to match desired schema
    df.rename(columns={
        'Date': 'timestamp',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Adj Close': 'adj_close',
        'Volume': 'volume'
    }, inplace=True)

    # Convert 'timestamp' to datetime format for MongoDB
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Add additional fields like P/E ratio
    df['pe_ratio'] = pe_ratio

    # Select relevant columns and handle missing or zero volume values
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'pe_ratio']]

    return df

def insert_into_mongodb(df):
    """Insert transformed data into MongoDB Atlas."""
    print("Connecting to MongoDB")
    
    # Convert DataFrame to Dictionary for MongoDB insertion
    records = df.to_dict(orient='records')

    # Insert records with upsert to avoid duplicates
    print(f"Inserting {len(records)} records into MongoDB")
    for record in records:
        # Ensure 'timestamp' is in the correct datetime format for MongoDB
        record['timestamp'] = pd.to_datetime(record['timestamp'])
        collection.update_one(
            {"timestamp": record["timestamp"]},
            {"$set": record},
            upsert=True
        )
    print("Data insertion complete")

def collect_data():
    """Main function to fetch, process, and store data."""
    # Fetch the last inserted date from MongoDB
    last_inserted_date = get_last_inserted_date()
    
    # Define the start and end date for data collection
    if last_inserted_date:
        start_date = (last_inserted_date + timedelta(days=1)).strftime('%Y-%m-%d')  # Start from the day after the last inserted date
    else:
        start_date = '2014-05-26'  # Default start date if no data is present

    end_date = datetime.today().strftime('%Y-%m-%d')  # Today's date
    
    # Fetch historical data
    raw_data = fetch_data(TICKER, start_date, end_date)

    # If there's no new data, stop the process
    if raw_data.empty:
        return {"message": "No new data to insert."}

    # Fetch additional info (P/E ratio)
    pe_ratio = fetch_additional_info(TICKER)

    # Clean and transform data
    clean_data = clean_transform_data(raw_data, pe_ratio)

    # Insert data into MongoDB
    insert_into_mongodb(clean_data)

    return {"message": f"Data from {start_date} to {end_date} collected and stored successfully."}
