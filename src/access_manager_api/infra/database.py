from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from access_manager_api.models import Base

# Create session factory without engine
SessionLocal = sessionmaker()
_engine = None


def init_db(database_url: str):
    """Initialize the database connection"""
    global _engine
    _engine = create_engine(database_url)
    SessionLocal.configure(bind=_engine)
    return _engine


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine():
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    return _engine


@contextmanager
def db_session_scope() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()