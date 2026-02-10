from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Identity, String, Boolean, text
from app.database import Base
from app.models.mixins import TimestampMixin


if TYPE_CHECKING:
    from app.models.order import Order

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), server_default=text("true"))
    orders: Mapped[list[Order]] = relationship(
        back_populates="user",
        lazy="selectin",  # <оптимально для коллекций(n+1)
        cascade="all, delete-orphan"
    )
