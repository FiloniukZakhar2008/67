"""initial schema with seed data

Revision ID: 20260517_0001
Revises:
Create Date: 2026-05-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260517_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bio", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    users = sa.table(
        "users",
        sa.column("id"),
        sa.column("name"),
        sa.column("email"),
        sa.column("hashed_password"),
        sa.column("age"),
    )
    categories = sa.table("categories", sa.column("id"), sa.column("name"), sa.column("description"))
    profiles = sa.table("profiles", sa.column("id"), sa.column("bio"), sa.column("phone"), sa.column("user_id"))
    products = sa.table(
        "products",
        sa.column("id"),
        sa.column("name"),
        sa.column("description"),
        sa.column("price"),
        sa.column("stock"),
        sa.column("category_id"),
    )
    posts = sa.table("posts", sa.column("id"), sa.column("title"), sa.column("content"), sa.column("author_id"))
    orders = sa.table("orders", sa.column("id"), sa.column("status"), sa.column("user_id"))
    order_items = sa.table("order_items", sa.column("id"), sa.column("quantity"), sa.column("product_id"), sa.column("order_id"))
    reviews = sa.table("reviews", sa.column("id"), sa.column("rating"), sa.column("comment"), sa.column("user_id"), sa.column("product_id"))

    op.bulk_insert(users, [
        {
            "id": 1,
            "name": "Zahar",
            "email": "zahar@example.com",
            "hashed_password": "pbkdf2_sha256$260000$29c017c051e61d3768811e222b3a6d0e$bf5ce77ecf888b28e9988361fd73bd3e21a63c2449c0ebafa56d9b522ea275ea",
            "age": 18,
        },
        {
            "id": 2,
            "name": "Anna",
            "email": "anna@example.com",
            "hashed_password": "pbkdf2_sha256$260000$2a6618e32d921a796823a2e7372b350b$275220302d79983a77b4a248b485ea65b4749a2bc9720852a743071f1a26caf4",
            "age": 21,
        },
    ])
    op.bulk_insert(categories, [
        {"id": 1, "name": "Blocks", "description": "Building materials and decorative blocks"},
        {"id": 2, "name": "Tools", "description": "Tools for mining and crafting"},
    ])
    op.bulk_insert(profiles, [
        {"id": 1, "bio": "Student and shop admin", "phone": "+380501112233", "user_id": 1},
        {"id": 2, "bio": "Regular customer", "phone": "+380671112233", "user_id": 2},
    ])
    op.bulk_insert(products, [
        {"id": 1, "name": "Minecraft Stone", "description": "Basic construction block", "price": 12.50, "stock": 64, "category_id": 1},
        {"id": 2, "name": "Diamond Pickaxe", "description": "Durable mining tool", "price": 199.99, "stock": 5, "category_id": 2},
    ])
    op.bulk_insert(posts, [
        {"id": 1, "title": "New tools arrived", "content": "Diamond tools are now available.", "author_id": 1},
        {"id": 2, "title": "Blocks discount", "content": "Stone blocks have a weekend discount.", "author_id": 2},
    ])
    op.bulk_insert(orders, [
        {"id": 1, "status": "paid", "user_id": 1},
        {"id": 2, "status": "new", "user_id": 2},
    ])
    op.bulk_insert(order_items, [
        {"id": 1, "quantity": 10, "product_id": 1, "order_id": 1},
        {"id": 2, "quantity": 1, "product_id": 2, "order_id": 2},
    ])
    op.bulk_insert(reviews, [
        {"id": 1, "rating": 5, "comment": "Very useful block set.", "user_id": 1, "product_id": 1},
        {"id": 2, "rating": 4, "comment": "Pickaxe is expensive but good.", "user_id": 2, "product_id": 2},
    ])


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_table("products")
    op.drop_table("posts")
    op.drop_table("profiles")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")