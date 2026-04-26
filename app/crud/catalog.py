from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from models import Category, Product
from schemas.product import Product as ProductSchema
from schemas.product import ProductCreate, ProductPage, ProductUpdate


def _apply_product_filters(
    stmt: Select,
    *,
    q: str | None = None,
    category_id: int | None = None,
    socket: str | None = None,
    min_power: float | None = None,
    max_power: float | None = None,
    min_brightness: int | None = None,
    max_brightness: int | None = None,
    color_temperature: int | None = None,
    shape: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
) -> Select:
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            or_(Product.name.ilike(pattern), Product.description.ilike(pattern))
        )
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if socket is not None:
        stmt = stmt.where(func.lower(Product.socket) == func.lower(socket))
    if min_power is not None:
        stmt = stmt.where(Product.power >= min_power)
    if max_power is not None:
        stmt = stmt.where(Product.power <= max_power)
    if min_brightness is not None:
        stmt = stmt.where(Product.brightness >= min_brightness)
    if max_brightness is not None:
        stmt = stmt.where(Product.brightness <= max_brightness)
    if color_temperature is not None:
        stmt = stmt.where(Product.color_temperature == color_temperature)
    if shape is not None:
        stmt = stmt.where(func.lower(Product.shape) == func.lower(shape))
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)
    return stmt


def _ordered(stmt: Select, sort: str) -> Select:
    s = sort.strip().lower()
    if s in ("popular", "popularity"):
        return stmt.order_by(Product.popularity.desc(), Product.id)
    if s == "price_asc":
        return stmt.order_by(Product.price.asc(), Product.id)
    if s == "price_desc":
        return stmt.order_by(Product.price.desc(), Product.id)
    if s == "name_asc":
        return stmt.order_by(Product.name.asc(), Product.id)
    if s == "name_desc":
        return stmt.order_by(Product.name.desc(), Product.id)
    if s == "newest":
        return stmt.order_by(Product.created_at.desc(), Product.id)
    return stmt.order_by(Product.popularity.desc(), Product.id)


def _to_schema(row: Product) -> ProductSchema:
    return ProductSchema.model_validate(row)


def search_products_page(
    db: Session,
    *,
    q: str | None = None,
    category_id: int | None = None,
    socket: str | None = None,
    min_power: float | None = None,
    max_power: float | None = None,
    min_brightness: int | None = None,
    max_brightness: int | None = None,
    color_temperature: int | None = None,
    shape: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "price_asc",
    page: int = 1,
    size: int = 20,
) -> ProductPage:
    base = select(Product)
    base = _apply_product_filters(
        base,
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
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    ordered = _ordered(base, sort)
    offset = (page - 1) * size
    rows = db.scalars(ordered.offset(offset).limit(size)).all()
    return ProductPage(
        items=[_to_schema(r) for r in rows],
        page=page,
        size=size,
        total=int(total),
    )


def list_products_page(
    db: Session,
    *,
    page: int = 1,
    size: int = 20,
    sort: str = "popular",
    category_id: int | None = None,
) -> ProductPage:
    return search_products_page(
        db,
        category_id=category_id,
        sort=sort,
        page=page,
        size=size,
    )


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def low_stock_products(db: Session, threshold: int) -> list[ProductSchema]:
    rows = db.scalars(
        select(Product).where(Product.quantity < threshold).order_by(Product.quantity, Product.id)
    ).all()
    return [_to_schema(r) for r in rows]


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.id)).all())


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def create_category(db: Session, name: str) -> Category:
    c = Category(name=name)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def update_category(db: Session, category_id: int, name: str) -> Category | None:
    c = db.get(Category, category_id)
    if c is None:
        return None
    c.name = name
    db.commit()
    db.refresh(c)
    return c


def delete_category(db: Session, category_id: int) -> tuple[bool, str | None]:
    c = db.get(Category, category_id)
    if c is None:
        return False, None
    has_products = db.scalar(
        select(func.count()).select_from(
            select(Product.id).where(Product.category_id == category_id).subquery()
        )
    )
    if has_products and int(has_products) > 0:
        return False, "В категории есть товары"
    db.delete(c)
    db.commit()
    return True, None


def create_product(db: Session, data: ProductCreate) -> Product | None:
    if db.get(Category, data.category_id) is None:
        return None
    p = Product(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product | None:
    p = db.get(Product, product_id)
    if p is None:
        return None
    if data.category_id is not None and db.get(Category, data.category_id) is None:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


def set_product_stock(db: Session, product_id: int, quantity: int) -> Product | None:
    p = db.get(Product, product_id)
    if p is None:
        return None
    p.quantity = quantity
    db.commit()
    db.refresh(p)
    return p


def delete_product(db: Session, product_id: int) -> bool:
    p = db.get(Product, product_id)
    if p is None:
        return False
    db.delete(p)
    db.commit()
    return True
