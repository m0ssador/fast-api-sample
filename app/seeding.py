from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Category, Product


def seed_catalog_if_empty(db: Session) -> None:
    if db.scalar(select(Category.id).limit(1)):
        return
    cat = Category(name="Бытовые лампы")
    db.add(cat)
    db.flush()
    db.add_all(
        [
            Product(
                category_id=cat.id,
                name="LED лампа 12W E27",
                description="Энергосберегающая лампа",
                price=320,
                quantity=1420,
                socket="E27",
                power=12,
                color_temperature=4000,
                brightness=1050,
                shape="груша",
                popularity=10,
            ),
            Product(
                category_id=cat.id,
                name="LED лампа 8W E14",
                description="Компактная свеча",
                price=210,
                quantity=5,
                socket="E14",
                power=8,
                color_temperature=2700,
                brightness=600,
                shape="свеча",
                popularity=4,
            ),
        ]
    )
    db.commit()
