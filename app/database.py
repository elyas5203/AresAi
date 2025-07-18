from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define the database file
DATABASE_URL = "sqlite:///./business_assistant.db"

# Create a new SQLAlchemy engine instance
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

def init_db():
    # Import all models here before calling Base.metadata.create_all
    # so that they will be registered properly on the metadata.
    # Otherwise you will have to import them first before calling init_db()
    from app.models import Competitor, AnalysisResult, Conversation
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    # This allows us to create the database from the command line
    init_db()
