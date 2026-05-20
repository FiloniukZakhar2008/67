from decimal import Decimal

import pytest

from app.core.security import verify_password
from app.crud import category, order, post, product, profile, review, user
from app.schemas.post import PostCreate, PostUpdate
from app.schemas.product import (
    CategoryCreate,
    CategoryUpdate,
    OrderCreate,
    OrderItemCreate,
    ProductCreate,
    ProductUpdate,
    ReviewCreate,
)
from app.schemas.user import ProfileCreate, ProfileUpdate, UserCreate, UserUpdate


pytestmark = pytest.mark.asyncio


async def create_db_user(db_session, email="crud-user@example.com"):
    return await user.create(
        db_session,
        UserCreate(name="CRUD User", email=email, password="secret123", age=25),
    )


async def create_db_category(db_session):
    return await category.create(
        db_session,
        CategoryCreate(name="CRUD Category", description="For tests"),
    )


async def create_db_product(db_session):
    db_category = await create_db_category(db_session)
    return await product.create(
        db_session,
        ProductCreate(
            name="CRUD Product",
            description="For tests",
            price=Decimal("10.50"),
            stock=3,
            category_id=db_category.id,
        ),
    )


async def test_user_crud_hashes_password_and_finds_by_email(db_session):
    created = await create_db_user(db_session)

    assert created.id is not None
    assert created.email == "crud-user@example.com"
    assert created.hashed_password != "secret123"
    assert verify_password("secret123", created.hashed_password)

    by_email = await user.get_by_email(db_session, "crud-user@example.com")
    assert by_email.id == created.id

    fetched = await user.get(db_session, created.id)
    assert fetched.id == created.id

    listed = await user.get_multi(db_session)
    assert [item.id for item in listed] == [created.id]

    updated = await user.update(db_session, created, UserUpdate(name="Renamed", age=30))
    assert updated.name == "Renamed"
    assert updated.age == 30

    removed = await user.remove(db_session, created.id)
    assert removed.id == created.id
    assert await user.get(db_session, created.id) is None


async def test_profile_crud(db_session):
    db_user = await create_db_user(db_session)
    created = await profile.create(
        db_session,
        ProfileCreate(bio="Bio", phone="+380001112233", user_id=db_user.id),
    )

    assert created.id is not None
    assert created.user_id == db_user.id
    assert (await profile.get(db_session, created.id)).bio == "Bio"
    assert len(await profile.get_multi(db_session)) == 1

    updated = await profile.update(db_session, created, ProfileUpdate(phone="+380009998877"))
    assert updated.phone == "+380009998877"

    assert (await profile.remove(db_session, created.id)).id == created.id
    assert await profile.remove(db_session, created.id) is None


async def test_post_crud(db_session):
    db_user = await create_db_user(db_session)
    created = await post.create(
        db_session,
        PostCreate(title="Post", content="Content", author_id=db_user.id),
    )

    assert created.id is not None
    assert (await post.get(db_session, created.id)).title == "Post"
    assert len(await post.get_multi(db_session)) == 1

    updated = await post.update(db_session, created, PostUpdate(content="Updated content"))
    assert updated.content == "Updated content"

    assert (await post.remove(db_session, created.id)).id == created.id
    assert await post.get(db_session, created.id) is None


async def test_category_get_multi(db_session):
    first = await create_db_category(db_session)
    second = await category.create(
        db_session,
        CategoryCreate(name="Second Category", description="Another one"),
    )

    listed = await category.get_multi(db_session)
    assert [item.id for item in listed] == [first.id, second.id]


async def test_category_and_product_crud(db_session):
    db_category = await create_db_category(db_session)
    assert db_category.id is not None
    assert (await category.get(db_session, db_category.id)).name == "CRUD Category"

    updated_category = await category.update(
        db_session,
        db_category,
        CategoryUpdate(description="Updated category"),
    )
    assert updated_category.description == "Updated category"

    created_product = await product.create(
        db_session,
        ProductCreate(
            name="Product",
            description="Description",
            price=Decimal("11.25"),
            stock=5,
            category_id=db_category.id,
        ),
    )
    assert created_product.id is not None
    assert (await product.get(db_session, created_product.id)).name == "Product"
    assert len(await product.get_multi(db_session)) == 1

    updated_product = await product.update(db_session, created_product, ProductUpdate(stock=12))
    assert updated_product.stock == 12

    assert (await product.remove(db_session, created_product.id)).id == created_product.id
    assert (await category.remove(db_session, db_category.id)).id == db_category.id


async def test_order_crud_creates_and_loads_items(db_session):
    db_user = await create_db_user(db_session)
    db_product = await create_db_product(db_session)

    created = await order.create(
        db_session,
        OrderCreate(
            user_id=db_user.id,
            status="new",
            items=[OrderItemCreate(product_id=db_product.id, quantity=2)],
        ),
    )

    assert created.id is not None
    assert created.items[0].product_id == db_product.id
    assert created.items[0].quantity == 2

    fetched = await order.get(db_session, created.id)
    assert fetched.items[0].quantity == 2

    listed = await order.get_multi(db_session)
    assert listed[0].items[0].product_id == db_product.id

    updated = await order.update(db_session, created, {"status": "paid"})
    assert updated.status == "paid"

    removed = await order.remove(db_session, created.id)
    assert removed.id == created.id
    assert await order.get(db_session, created.id) is None
    assert await order.remove(db_session, created.id) is None


async def test_review_crud(db_session):
    db_user = await create_db_user(db_session)
    db_product = await create_db_product(db_session)
    created = await review.create(
        db_session,
        ReviewCreate(rating=4, comment="Good", user_id=db_user.id, product_id=db_product.id),
    )

    assert created.id is not None
    assert (await review.get(db_session, created.id)).rating == 4
    assert len(await review.get_multi(db_session)) == 1

    updated = await review.update(
        db_session,
        created,
        ReviewCreate(rating=5, comment="Excellent", user_id=db_user.id, product_id=db_product.id),
    )
    assert updated.rating == 5
    assert updated.comment == "Excellent"

    assert (await review.remove(db_session, created.id)).id == created.id
    assert await review.get(db_session, created.id) is None
