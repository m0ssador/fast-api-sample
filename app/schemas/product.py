from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Название")
    price: float = Field(..., gt=0, description="Цена")
    description: str | None = Field(None, max_length=2000, description="Описание")


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int = Field(..., ge=1)

    model_config = ConfigDict(from_attributes=True)
