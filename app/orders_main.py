from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from db.session import Base, engine
from models import Category, Order, OrderItem, Product  # noqa: F401 — регистрация ORM
from routers import orders


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="BulbStore — заказы",
    description="Создание заказов, список, смена статуса (остатки на каталоге).",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(orders.router, prefix="/orders")


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "service": "orders"}
