from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryRead(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    stock: int = 0
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    category_id: int | None = None


class ProductRead(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class OrderItemRead(OrderItemCreate):
    id: int
    order_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    user_id: int
    status: str = "new"
    items: list[OrderItemCreate]


class OrderRead(BaseModel):
    id: int
    user_id: int
    status: str
    items: list[OrderItemRead] = []

    model_config = ConfigDict(from_attributes=True)


class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    user_id: int
    product_id: int


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: int

    model_config = ConfigDict(from_attributes=True)