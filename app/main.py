from contextlib import asynccontextmanager

from fastapi import FastAPI

from memory_catalog import seed_demo
from routers import catalog

API_PREFIX = "/catalog"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    seed_demo()
    yield


app = FastAPI(
    title="BulbStore catalog (прототип)",
    description="In-memory API по структуре BulbStore_postman.json (без БД).",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(catalog.router, prefix=API_PREFIX)


@app.get("/")
def read_root():
    return {
        "message": "Каталог: префикс /catalog (как baseUrl в Postman). Документация: /docs",
    }
