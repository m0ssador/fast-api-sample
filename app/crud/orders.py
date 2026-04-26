from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from models import Order, OrderItem, Product
from schemas.order import OrderCreate, OrderItemOut, OrderOut, OrderPage

_VALID_TRANSITIONS = frozenset(
    {
        ("pending", "confirmed"),
        ("pending", "cancelled"),
        ("confirmed", "shipped"),
        ("confirmed", "cancelled"),
    }
)


def _load_order(db: Session, order_id: int) -> Order | None:
    return db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
    ).unique().scalar_one_or_none()


def order_to_out(order: Order) -> OrderOut:
    items_out: list[OrderItemOut] = []
    for it in order.items:
        name = it.product.name if it.product else ""
        items_out.append(
            OrderItemOut(
                id=it.id,
                product_id=it.product_id,
                product_name=name,
                quantity=it.quantity,
                unit_price=it.unit_price,
            )
        )
    return OrderOut(
        id=order.id,
        status=order.status,
        customer_email=order.customer_email,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items_out,
    )


def create_order(db: Session, payload: OrderCreate) -> Order:
    pairs = [(it.product_id, it.quantity) for it in payload.items]
    if not pairs:
        raise ValueError("empty_order")

    for pid, qty in pairs:
        row = db.execute(
            select(Product).where(Product.id == pid).with_for_update()
        ).scalar_one_or_none()
        if row is None:
            raise ValueError(f"product_not_found:{pid}")
        if row.quantity < qty:
            raise ValueError(f"insufficient_stock:{pid}")

    order = Order(status="pending", customer_email=payload.customer_email)
    db.add(order)
    db.flush()

    for pid, qty in pairs:
        row = db.execute(
            select(Product).where(Product.id == pid).with_for_update()
        ).scalar_one()
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=pid,
                quantity=qty,
                unit_price=row.price,
            )
        )
        row.quantity -= qty

    order.updated_at = datetime.now(timezone.utc)
    db.commit()
    loaded = _load_order(db, order.id)
    assert loaded is not None
    return loaded


def get_order(db: Session, order_id: int) -> Order | None:
    return _load_order(db, order_id)


def list_orders_page(db: Session, *, page: int = 1, size: int = 20) -> OrderPage:
    total = db.scalar(select(func.count()).select_from(Order.__table__)) or 0
    offset = (page - 1) * size
    stmt = (
        select(Order)
        .order_by(Order.id.desc())
        .offset(offset)
        .limit(size)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
    )
    rows = db.execute(stmt).unique().scalars().all()
    return OrderPage(
        items=[order_to_out(o) for o in rows],
        page=page,
        size=size,
        total=int(total),
    )


def update_order_status(db: Session, order_id: int, new_status: str) -> Order | None:
    order = db.execute(
        select(Order).where(Order.id == order_id).with_for_update()
    ).scalar_one_or_none()
    if order is None:
        return None

    items = list(
        db.scalars(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    )

    old = order.status
    if old == new_status:
        return _load_order(db, order_id)

    if old == "cancelled":
        raise ValueError("order_already_cancelled")

    if (old, new_status) not in _VALID_TRANSITIONS:
        raise ValueError("invalid_transition")

    if new_status == "cancelled":
        for it in items:
            row = db.execute(
                select(Product).where(Product.id == it.product_id).with_for_update()
            ).scalar_one_or_none()
            if row is not None:
                row.quantity += it.quantity

    order.status = new_status
    order.updated_at = datetime.now(timezone.utc)
    db.commit()
    return _load_order(db, order_id)
