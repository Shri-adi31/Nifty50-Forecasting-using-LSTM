from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import historical, forecast
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],  # Default is localhost, can be overridden in .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(historical.router, prefix="/api")
app.include_router(forecast.router, prefix="/api")

# Run the server: uvicorn app.main:app --reload
