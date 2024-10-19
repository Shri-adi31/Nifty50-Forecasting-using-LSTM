import json
import yfinance as yf
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
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

    # Convert 'timestamp' to only the date part for MongoDB
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date

    # Add additional fields like P/E ratio
    df['pe_ratio'] = pe_ratio

    # Select relevant columns and handle missing or zero volume values
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'pe_ratio']]

    return df

def save_data_as_json(data, filename=JSON_OUTPUT_FILE):
    """Save DataFrame to a JSON file."""
    # Convert DataFrame to Dictionary
    records = data.to_dict(orient='records')
    
    # Save data to JSON file
    with open(filename, 'w') as file:
        json.dump(records, file, indent=4, default=str)  # Ensure datetime is saved as string

    print(f"Data saved to {filename}")

def insert_json_into_mongodb(json_file):
    """Insert data from JSON file into MongoDB Atlas."""
    print(f"Inserting data from {json_file} into MongoDB")
    
    # Read the JSON file
    with open(json_file, 'r') as file:
        records = json.load(file)
    
    # Insert records into MongoDB
    print(f"Inserting {len(records)} records into MongoDB")
    collection.insert_many(records)
    print("Data insertion complete")

def collect_data():
    """Main function to fetch, process, and store data."""
    # Define the start and end date for data collection
    start_date = '2014-05-26'  # Default start date
    end_date = datetime.today().strftime('%Y-%m-%d')  # Today's date
    
    # Fetch historical data
    raw_data = fetch_data(TICKER, start_date, end_date)

    # If there's no data, stop the process
    if raw_data.empty:
        return {"message": "No data to insert."}

    # Fetch additional info (P/E ratio)
    pe_ratio = fetch_additional_info(TICKER)

    # Clean and transform data
    clean_data = clean_transform_data(raw_data, pe_ratio)

    # Save data to JSON file
    save_data_as_json(clean_data)

    # Insert data into MongoDB from JSON file
    insert_json_into_mongodb(JSON_OUTPUT_FILE)

    return {"message": f"Data from {start_date} to {end_date} collected and stored successfully."}

# Execute the data collection process
if __name__ == "__main__":
    result = collect_data()
    print(result)
