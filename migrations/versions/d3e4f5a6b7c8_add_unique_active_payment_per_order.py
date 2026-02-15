"""add unique active payment per order

Revision ID: d3e4f5a6b7c8
Revises: c2f1d7f3aa10
Create Date: 2026-02-15 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "c2f1d7f3aa10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_payments_active_per_order",
        "payments",
        ["order_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('CREATED', 'PENDING')"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_payments_active_per_order", table_name="payments")
