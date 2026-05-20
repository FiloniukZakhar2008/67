from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import category, order, product, review
from app.core.metrics import record_order_metrics
from app.db.session import get_db
from app.schemas.product import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    OrderCreate,
    OrderRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ReviewCreate,
    ReviewRead,
)

router = APIRouter()


@router.get("/categories/", response_model=list[CategoryRead])
async def read_categories(db: AsyncSession = Depends(get_db)):
    return await category.get_multi(db)


@router.post("/categories/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(obj_in: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await category.create(db, obj_in)


@router.patch("/categories/{category_id}", response_model=CategoryRead)
async def update_category(category_id: int, obj_in: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    db_category = await category.get(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return await category.update(db, db_category, obj_in)


@router.get("/orders/", response_model=list[OrderRead])
async def read_orders(db: AsyncSession = Depends(get_db)):
    return await order.get_multi(db)


@router.post("/orders/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(obj_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    db_order = await order.create(db, obj_in)
    await record_order_metrics(db, db_order.id)
    return db_order


@router.get("/reviews/", response_model=list[ReviewRead])
async def read_reviews(db: AsyncSession = Depends(get_db)):
    return await review.get_multi(db)


@router.post("/reviews/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(obj_in: ReviewCreate, db: AsyncSession = Depends(get_db)):
    return await review.create(db, obj_in)


@router.get("/", response_model=list[ProductRead])
async def read_products(db: AsyncSession = Depends(get_db)):
    return await product.get_multi(db)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(obj_in: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await product.create(db, obj_in)


@router.get("/{product_id}", response_model=ProductRead)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product = await product.get(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(product_id: int, obj_in: ProductUpdate, db: AsyncSession = Depends(get_db)):
    db_product = await product.get(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return await product.update(db, db_product, obj_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await product.remove(db, product_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Product not found")