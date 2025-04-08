from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from access_manager_api.config import settings
from access_manager_api.models import Base

# Create engine and session factory
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine():
    return engine
