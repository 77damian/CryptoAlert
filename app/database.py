from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# Create the database engine using the URL from .env (default: sqlite:///./cryptoalert.db)
# connect_args={"check_same_thread": False} is required only for SQLite with FastAPI
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass


def get_db():
    """FastAPI dependency – provides a database session to endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
