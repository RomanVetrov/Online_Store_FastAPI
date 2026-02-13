"""add payments table

Revision ID: c2f1d7f3aa10
Revises: 91c428cb3f75
Create Date: 2026-02-13 20:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2f1d7f3aa10"
down_revision: Union[str, Sequence[str], None] = "91c428cb3f75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "CREATED",
                "PENDING",
                "SUCCEEDED",
                "FAILED",
                "CANCELED",
                name="paymentstatus",
            ),
            nullable=False,
        ),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=128), nullable=True),
        sa.Column("checkout_url", sa.String(length=1024), nullable=True),
        sa.Column("fail_reason", sa.String(length=255), nullable=True),
        sa.Column("provider_payload", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index(
        op.f("ix_payments_order_id"), "payments", ["order_id"], unique=False
    )
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)
    op.create_index(
        "ix_payments_order_status",
        "payments",
        ["order_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_payments_provider_payment_id",
        "payments",
        ["provider_payment_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_payments_provider_payment_id", table_name="payments")
    op.drop_index("ix_payments_order_status", table_name="payments")
    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_order_id"), table_name="payments")
    op.drop_table("payments")
