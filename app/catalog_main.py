from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from db.session import Base, engine
from deps import SessionLocal
from models import Category, Order, OrderItem, Product  # noqa: F401 — регистрация ORM
from routers import catalog
from seeding import seed_catalog_if_empty


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_catalog_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="BulbStore — каталог",
    description="Каталог товаров (прототип BulbStore_postman.json) + PostgreSQL.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(catalog.router, prefix="/catalog")


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "service": "catalog"}
