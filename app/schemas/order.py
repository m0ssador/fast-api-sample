from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

OrderStatus = Literal["pending", "confirmed", "shipped", "cancelled"]


class OrderItemCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1)


class OrderCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    items: list[OrderItemCreate]
    customer_email: str | None = Field(None, max_length=255, alias="customerEmail")


class OrderItemOut(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float


class OrderOut(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    status: str
    customer_email: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut]


class OrderPage(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    items: list[OrderOut]
    page: int
    size: int
    total: int


class OrderStatusUpdate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    status: OrderStatus
