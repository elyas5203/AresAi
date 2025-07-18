import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get MySQL credentials from environment variables
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "business_assistant")

# Define the database URL for MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Create a new SQLAlchemy engine instance
engine = create_engine(DATABASE_URL)

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

def init_db():
    # Import all models here before calling Base.metadata.create_all
    from app.models import Competitor, AnalysisResult, Conversation
    print("Creating database and tables if they don't exist...")
    # This will create the database if it doesn't exist
    try:
        engine.connect()
    except Exception as e:
        if "1049" in str(e): # Database does not exist
            print(f"Database '{DB_NAME}' does not exist. Please create it first.")
            # Or you can create it programmatically, but that requires admin privileges
            # For simplicity, we'll ask the user to create it.
            return
        raise e

    Base.metadata.create_all(bind=engine)
    print("Database tables are ready.")

if __name__ == "__main__":
    init_db()
