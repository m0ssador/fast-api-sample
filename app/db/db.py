import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "super_secret_password")
DB_HOST = "postgres_db" #os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "shop")
#DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
