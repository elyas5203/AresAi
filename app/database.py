import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get MySQL credentials from environment variables
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "business_assistant")

# Connection URL without the database name to check for its existence
SERVER_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}"
DATABASE_URL = f"{SERVER_URL}/{DB_NAME}"

# Create engines
server_engine = create_engine(SERVER_URL)
engine = create_engine(DATABASE_URL)

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

def init_db():
    """
    Initializes the database. Creates the database if it does not exist,
    then creates all tables.
    """
    from app.models import Competitor, AnalysisResult, Conversation

    try:
        # Try to connect to the specific database
        with engine.connect() as connection:
            print(f"Successfully connected to database '{DB_NAME}'.")
    except Exception as e:
        # If connection fails, it might be because the database doesn't exist
        if "1049" in str(e):
            print(f"Database '{DB_NAME}' not found. Attempting to create it...")
            try:
                with server_engine.connect() as connection:
                    connection.execute(text(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    print(f"Database '{DB_NAME}' created successfully.")
            except Exception as create_error:
                print(f"Failed to create database '{DB_NAME}': {create_error}")
                return # Stop if we can't create the DB
        else:
            # For other connection errors, just raise them
            print(f"An unexpected error occurred: {e}")
            raise e

    # Now, create all tables in the (now existing) database
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables are ready.")

if __name__ == "__main__":
    init_db()
