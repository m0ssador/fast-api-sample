from fastapi import APIRouter, HTTPException, Query

from memory_catalog import (
    filter_products,
    get_product,
    list_categories,
    paginate,
    sort_products,
)
from schemas.category import Category
from schemas.product import (
    Product,
    ProductAvailability,
    ProductPage,
)

router = APIRouter(tags=["BulbStore catalog"])


@router.get("/products/search", response_model=ProductPage)
def search_products(
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
    filtered = filter_products(
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
    )
    ordered = sort_products(filtered, sort)
    items, total = paginate(ordered, page, size)
    return ProductPage(items=items, page=page, size=size, total=total)


# --- Админ-интерфейс (закомментировано) ---
#
# @router.get("/products/low-stock", response_model=list[Product])
# def get_low_stock_products(
#     threshold: int = Query(10, ge=0, description="Порог остатка"),
# ) -> list[Product]:
#     return low_stock(threshold)
#
#
# @router.post("/products", response_model=Product, status_code=201)
# def admin_create_product(
#     payload: ProductCreate,
# ) -> Product:
#     if get_category(payload.category_id) is None:
#         raise HTTPException(status_code=400, detail="Категория не найдена")
#     created = create_product(payload)
#     if created is None:
#         raise HTTPException(status_code=400, detail="Категория не найдена")
#     return created
#
#
# @router.patch("/products/{product_id}", response_model=Product)
# def admin_update_product(
#     product_id: int,
#     payload: ProductUpdate,
# ) -> Product:
#     if get_product(product_id) is None:
#         raise HTTPException(status_code=404, detail="Товар не найден")
#     if payload.category_id is not None and get_category(payload.category_id) is None:
#         raise HTTPException(status_code=400, detail="Категория не найдена")
#     updated = update_product(product_id, payload)
#     if updated is None:
#         raise HTTPException(status_code=404, detail="Товар не найден")
#     return updated
#
#
# @router.patch("/products/{product_id}/stock", response_model=Product)
# def admin_update_product_stock(
#     product_id: int,
#     payload: StockUpdate,
# ) -> Product:
#     updated = set_product_stock(product_id, payload.quantity)
#     if updated is None:
#         raise HTTPException(status_code=404, detail="Товар не найден")
#     return updated
#
#
# @router.delete("/products/{product_id}", status_code=204)
# def admin_delete_product(
#     product_id: int,
# ) -> None:
#     if not delete_product(product_id):
#         raise HTTPException(status_code=404, detail="Товар не найден")
#
#
# @router.post("/categories", response_model=Category, status_code=201)
# def admin_create_category(
#     payload: CategoryCreate,
# ) -> Category:
#     return create_category(payload)
#
#
# @router.patch("/categories/{category_id}", response_model=Category)
# def admin_update_category(
#     category_id: int,
#     payload: CategoryUpdate,
# ) -> Category:
#     updated = update_category(category_id, payload)
#     if updated is None:
#         raise HTTPException(status_code=404, detail="Категория не найдена")
#     return updated
#
#
# @router.delete("/categories/{category_id}", status_code=204)
# def admin_delete_category(
#     category_id: int,
# ) -> None:
#     ok, reason = delete_category(category_id)
#     if not ok and reason is None:
#         raise HTTPException(status_code=404, detail="Категория не найдена")
#     if not ok:
#         raise HTTPException(status_code=409, detail=reason)


@router.get("/products", response_model=ProductPage)
def get_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort: str = Query("popular", description="popular, price_asc, price_desc, ..."),
    category_id: int | None = Query(None, alias="categoryId"),
) -> ProductPage:
    filtered = filter_products(category_id=category_id)
    ordered = sort_products(filtered, sort)
    items, total = paginate(ordered, page, size)
    return ProductPage(items=items, page=page, size=size, total=total)


@router.get("/categories", response_model=list[Category])
def get_categories() -> list[Category]:
    return list_categories()


@router.get("/products/{product_id}/availability", response_model=ProductAvailability)
def check_product_availability(
    product_id: int,
    quantity: int = Query(1, ge=1, description="Проверяемое количество"),
) -> ProductAvailability:
    p = get_product(product_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return ProductAvailability(
        product_id=p.id,
        requested_quantity=quantity,
        available=p.quantity >= quantity,
        stock_quantity=p.quantity,
    )


@router.get("/products/{product_id}", response_model=Product)
def get_product_by_id(product_id: int) -> Product:
    p = get_product(product_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return p
