from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(4000))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    socket: Mapped[str] = mapped_column(String(32), nullable=False)
    power: Mapped[float] = mapped_column(Float, nullable=False)
    color_temperature: Mapped[int] = mapped_column(Integer, nullable=False)
    brightness: Mapped[int] = mapped_column(Integer, nullable=False)
    shape: Mapped[str] = mapped_column(String(64), nullable=False)
    popularity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    category: Mapped["Category"] = relationship(back_populates="products")
