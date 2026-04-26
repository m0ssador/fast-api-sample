import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def _default_database_url() -> str:
    user = os.getenv("POSTGRES_USER", "user")
    password = os.getenv("POSTGRES_PASSWORD", "super_secret_password")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    name = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "shop"))
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


DATABASE_URL = os.getenv("DATABASE_URL", _default_database_url())
if DATABASE_URL.startswith("postgresql://") and "+" not in DATABASE_URL.split("://", 1)[0]:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
