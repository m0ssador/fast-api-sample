from fastapi import FastAPI, HTTPException

from schemas.product import Product, ProductCreate

app = FastAPI(
    title="Пример FastAPI",
    description="Простое in-memory API товаров",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Привет! Интерактивная документация: /docs и /redoc"}


products: list[Product] = []
_next_id: int = 1


@app.post("/products", response_model=Product, status_code=201)
def add_product(payload: ProductCreate) -> Product:
    global _next_id
    product = Product(id=_next_id, **payload.model_dump())
    _next_id += 1
    products.append(product)
    return product


@app.get("/products", response_model=list[Product])
def list_products() -> list[Product]:
    return products


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int) -> Product:
    for item in products:
        if item.id == product_id:
            return item
    raise HTTPException(status_code=404, detail="Товар не найден")
