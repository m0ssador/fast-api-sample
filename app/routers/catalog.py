from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import crud.catalog as catalog_crud
from deps import get_db
from schemas.category import Category, CategoryCreate, CategoryUpdate
from schemas.product import (
    Product,
    ProductAvailability,
    ProductCreate,
    ProductPage,
    ProductUpdate,
    StockUpdate,
)

router = APIRouter(tags=["BulbStore catalog"])


def _product_schema(row) -> Product:
    return Product.model_validate(row)


@router.get("/products/search", response_model=ProductPage)
def search_products(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Поиск по названию и описанию"),
    category_id: int | None = Query(None, alias="categoryId", description="ID категории"),
    socket: str | None = Query(None, description="Цоколь (E27, E14, GU10, G9 и др.)"),
    min_power: float | None = Query(None, alias="minPower", description="Мин. мощность (Вт)"),
    max_power: float | None = Query(None, alias="maxPower", description="Макс. мощность (Вт)"),
    min_brightness: int | None = Query(
        None, alias="minBrightness", description="Мин. яркость (лм)"
    ),
    max_brightness: int | None = Query(
        None, alias="maxBrightness", description="Макс. яркость (лм)"
    ),
    color_temperature: int | None = Query(
        None, alias="colorTemperature", description="Цветовая температура (К)"
    ),
    shape: str | None = Query(None, description="Форма (груша, свеча, шар, труба)"),
    min_price: float | None = Query(None, alias="minPrice", description="Мин. цена"),
    max_price: float | None = Query(None, alias="maxPrice", description="Макс. цена"),
    sort: str = Query(
        "price_asc",
        description="Сортировка: price_asc, price_desc, name_asc, name_desc, popularity, newest",
    ),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=200, description="Размер страницы"),
) -> ProductPage:
    return catalog_crud.search_products_page(
        db,
        q=q,
        category_id=category_id,
        socket=socket,
        min_power=min_power,
        max_power=max_power,
        min_brightness=min_brightness,
        max_brightness=max_brightness,
        color_temperature=color_temperature,
        shape=shape,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        size=size,
    )


@router.get("/products/low-stock", response_model=list[Product])
def get_low_stock_products(
    db: Session = Depends(get_db),
    threshold: int = Query(10, ge=0, description="Порог остатка"),
) -> list[Product]:
    return catalog_crud.low_stock_products(db, threshold)


@router.get("/products", response_model=ProductPage)
def get_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort: str = Query("popular", description="popular, price_asc, price_desc, ..."),
    category_id: int | None = Query(None, alias="categoryId"),
) -> ProductPage:
    return catalog_crud.list_products_page(
        db, page=page, size=size, sort=sort, category_id=category_id
    )


@router.get("/categories", response_model=list[Category])
def get_categories(db: Session = Depends(get_db)) -> list[Category]:
    return catalog_crud.list_categories(db)


@router.get("/products/{product_id}/availability", response_model=ProductAvailability)
def check_product_availability(
    product_id: int,
    db: Session = Depends(get_db),
    quantity: int = Query(1, ge=1, description="Проверяемое количество"),
) -> ProductAvailability:
    p = catalog_crud.get_product_by_id(db, product_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return ProductAvailability(
        product_id=p.id,
        requested_quantity=quantity,
        available=p.quantity >= quantity,
        stock_quantity=p.quantity,
    )


@router.get("/products/{product_id}", response_model=Product)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> Product:
    p = catalog_crud.get_product_by_id(db, product_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return _product_schema(p)


@router.post("/products", response_model=Product, status_code=201)
def admin_create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    if catalog_crud.get_category(db, payload.category_id) is None:
        raise HTTPException(status_code=400, detail="Категория не найдена")
    created = catalog_crud.create_product(db, payload)
    if created is None:
        raise HTTPException(status_code=400, detail="Категория не найдена")
    return _product_schema(created)


@router.patch("/products/{product_id}", response_model=Product)
def admin_update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
) -> Product:
    if catalog_crud.get_product_by_id(db, product_id) is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if payload.category_id is not None and catalog_crud.get_category(db, payload.category_id) is None:
        raise HTTPException(status_code=400, detail="Категория не найдена")
    updated = catalog_crud.update_product(db, product_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return _product_schema(updated)


@router.patch("/products/{product_id}/stock", response_model=Product)
def admin_update_product_stock(
    product_id: int,
    payload: StockUpdate,
    db: Session = Depends(get_db),
) -> Product:
    updated = catalog_crud.set_product_stock(db, product_id, payload.quantity)
    if updated is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return _product_schema(updated)


@router.delete("/products/{product_id}", status_code=204)
def admin_delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    if not catalog_crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Товар не найден")


@router.post("/categories", response_model=Category, status_code=201)
def admin_create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    return catalog_crud.create_category(db, payload.name)


@router.patch("/categories/{category_id}", response_model=Category)
def admin_update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
) -> Category:
    updates = payload.model_dump(exclude_unset=True)
    if "name" not in updates or updates["name"] is None:
        raise HTTPException(status_code=400, detail="Укажите поле name")
    updated = catalog_crud.update_category(db, category_id, updates["name"])
    if updated is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return updated


@router.delete("/categories/{category_id}", status_code=204)
def admin_delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    ok, reason = catalog_crud.delete_category(db, category_id)
    if not ok and reason is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    if not ok:
        raise HTTPException(status_code=409, detail=reason)
