"""
Test database connection
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file!")
    print("Make sure .env file exists with DATABASE_URL variable")
    exit(1)

print(f"Connecting to: {DATABASE_URL[:40]}...")

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print("\n✅ Database connection successful!")
        print(f"PostgreSQL version: {version[:80]}...")
        
        # Test current database
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"Connected to database: {db_name}")
        
except Exception as e:
    print("\n❌ Database connection failed!")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. PostgreSQL is not running")
    print("2. Wrong password in DATABASE_URL")
    print("3. Database 'pharma_db' doesn't exist")