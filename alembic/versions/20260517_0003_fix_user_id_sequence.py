"""fix user id sequence after seed data

Revision ID: 20260517_0003
Revises: 20260517_0002
Create Date: 2026-05-17
"""
from typing import Sequence, Union

from alembic import op

revision: str = "20260517_0003"
down_revision: Union[str, None] = "20260517_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1), true)")


def downgrade() -> None:
    pass