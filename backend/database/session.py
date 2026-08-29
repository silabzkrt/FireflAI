"""
FireflAI - Database Engine & Session Management

Configures the PostgreSQL / SQLite database connection, engine initialization, sessionmaker,
and provides the FastAPI dependency generator for database session lifecycle handling.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:5126@localhost:5432/firefl_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()