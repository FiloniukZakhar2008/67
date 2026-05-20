from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.product import Category, Order, OrderItem, Product, Review
from app.schemas.product import (
    CategoryCreate,
    CategoryUpdate,
    OrderCreate,
    ProductCreate,
    ProductUpdate,
    ReviewCreate,
)


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderCreate]):
    async def get(self, db: AsyncSession, id: int) -> Order | None:
        result = await db.execute(select(Order).options(selectinload(Order.items)).where(Order.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Order]:
        result = await db.execute(select(Order).options(selectinload(Order.items)).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: OrderCreate) -> Order:
        data = obj_in.model_dump()
        items = data.pop("items")
        order = Order(**data)
        order.items = [OrderItem(**item) for item in items]
        db.add(order)
        await db.commit()
        await db.refresh(order, attribute_names=["items"])
        return order


category = CRUDBase[Category, CategoryCreate, CategoryUpdate](Category)
product = CRUDBase[Product, ProductCreate, ProductUpdate](Product)
order = CRUDOrder(Order)
review = CRUDBase[Review, ReviewCreate, ReviewCreate](Review)