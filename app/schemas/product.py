from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ProductBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=4000)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    category_id: int = Field(..., ge=1)
    socket: str = Field(..., min_length=1, max_length=32)
    power: float = Field(..., gt=0)
    color_temperature: int = Field(..., gt=0)
    brightness: int = Field(..., ge=0)
    shape: str = Field(..., min_length=1, max_length=64)
    popularity: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int = Field(..., ge=1)
    created_at: datetime

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class ProductUpdate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=4000)
    price: float | None = Field(None, gt=0)
    quantity: int | None = Field(None, ge=0)
    category_id: int | None = Field(None, ge=1)
    socket: str | None = Field(None, min_length=1, max_length=32)
    power: float | None = Field(None, gt=0)
    color_temperature: int | None = Field(None, gt=0)
    brightness: int | None = Field(None, ge=0)
    shape: str | None = Field(None, min_length=1, max_length=64)
    popularity: int | None = Field(None, ge=0)


class StockUpdate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    quantity: int = Field(..., ge=0)
    operation: Literal["SET"] = "SET"


class ProductPage(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    items: list[Product]
    page: int
    size: int
    total: int


class ProductAvailability(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    product_id: int
    requested_quantity: int
    available: bool
    stock_quantity: int
