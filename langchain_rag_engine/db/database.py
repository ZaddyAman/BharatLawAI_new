from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

# Check for Railway PostgreSQL DATABASE_URL first, fallback to SQLite for local development
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Railway PostgreSQL database - optimized for Railway
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    print(f"[DATABASE] Using Railway PostgreSQL database")
    print(f"[DATABASE] DATABASE_URL: {DATABASE_URL[:50]}...")

    # Railway-optimized connection settings
    connect_args = {
        "connect_timeout": 10,
        "pool_timeout": 30,
        "pool_recycle": 300,  # Recycle connections every 5 minutes
        "application_name": "bharatlaw-backend"
    }

    # Create engine with Railway-optimized pool settings
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,          # Smaller pool for Railway
        max_overflow=10,      # Allow overflow but limit it
        pool_timeout=30,
        pool_recycle=300,     # Recycle every 5 minutes
        pool_pre_ping=True,   # Test connections before use
        connect_args=connect_args,
        echo=False
    )

else:
    # Local SQLite fallback
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_PATH = os.path.join(PROJECT_ROOT, "sql_app.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    print(f"[DATABASE] Using local SQLite database at: {DATABASE_PATH}")
    print(f"[DATABASE] File exists: {os.path.exists(DATABASE_PATH)}")
    print(f"[DATABASE] Current working directory: {os.getcwd()}")
    connect_args = {"check_same_thread": False}

    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    import langchain_rag_engine.db.models as models
    Base.metadata.create_all(bind=engine)
