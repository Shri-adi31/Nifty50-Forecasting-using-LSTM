# app/database.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the MongoDB connection string from the environment variables
MONGO_URI = os.getenv("MONGO_URI")

# Create MongoDB client
client = MongoClient(MONGO_URI)
db = client["finance_app"]  # Replace with your actual database name

def get_collection(collection_name):
    return db[collection_name]
