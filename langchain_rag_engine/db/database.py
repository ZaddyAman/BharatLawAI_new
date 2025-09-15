from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

import os

# Railway provides DATABASE_URL environment variable for Postgres
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # Fallback for local development (SQLite)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_PATH = os.path.join(PROJECT_ROOT, "sql_app.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    print(f"[DATABASE] Using SQLite fallback at: {DATABASE_PATH}")
else:
    print(f"[DATABASE] Using Railway Postgres database")

print(f"[DATABASE] Database URL configured: {'Yes' if SQLALCHEMY_DATABASE_URL else 'No'}")

# Create engine with connection pooling for Railway
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Postgres configuration for Railway
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        echo=False  # Disable SQL logging in production
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)
