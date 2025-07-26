from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///libraflux.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)  # necessário p/ SQLite
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False)
)
Base = declarative_base()
