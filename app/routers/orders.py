from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import crud.orders as orders_crud
from deps import get_db
from schemas.order import OrderCreate, OrderOut, OrderPage, OrderStatusUpdate

router = APIRouter(tags=["BulbStore orders"])


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> OrderOut:
    try:
        order = orders_crud.create_order(db, payload)
    except ValueError as e:
        msg = str(e)
        if msg.startswith("product_not_found"):
            raise HTTPException(status_code=404, detail="Товар не найден") from e
        if msg.startswith("insufficient_stock"):
            raise HTTPException(status_code=409, detail="Недостаточно товара на складе") from e
        if msg == "empty_order":
            raise HTTPException(status_code=400, detail="Пустой заказ") from e
        raise HTTPException(status_code=400, detail=msg) from e
    return orders_crud.order_to_out(order)


@router.get("/", response_model=OrderPage)
def list_orders(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
) -> OrderPage:
    return orders_crud.list_orders_page(db, page=page, size=size)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderOut:
    order = orders_crud.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return orders_crud.order_to_out(order)


@router.patch("/{order_id}/status", response_model=OrderOut)
def patch_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
) -> OrderOut:
    try:
        order = orders_crud.update_order_status(db, order_id, payload.status)
    except ValueError as e:
        msg = str(e)
        if msg == "order_already_cancelled":
            raise HTTPException(status_code=409, detail="Заказ уже отменён") from e
        if msg == "invalid_transition":
            raise HTTPException(status_code=400, detail="Недопустимое изменение статуса") from e
        raise HTTPException(status_code=400, detail=msg) from e
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return orders_crud.order_to_out(order)
