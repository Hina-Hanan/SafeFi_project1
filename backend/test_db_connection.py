# backend/test_db_connection.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to: {DATABASE_URL}")

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"✅ Database connected successfully!")
        print(f"PostgreSQL version: {version[0]}")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("Check your DATABASE_URL in .env file")
