import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:root@localhost:5432/delivery_system')

# Application configuration
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))

# Business rules
MAX_WORKING_HOURS = 10  # hours
MAX_DAILY_DISTANCE = 100  # kilometers
TRAVEL_TIME_PER_KM = 5  # minutes

# Payment structure
BASE_PAY = 500  # INR
ORDERS_25_PLUS_RATE = 35  # INR per order
ORDERS_50_PLUS_RATE = 42  # INR per order 