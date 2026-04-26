from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CategoryBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str = Field(..., min_length=1, max_length=200)


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int = Field(..., ge=1)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str | None = Field(None, min_length=1, max_length=200)
