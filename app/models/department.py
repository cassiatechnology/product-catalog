from __future__ import annotations
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    categories: Mapped[list["Category"]] = relationship("Category", back_populates="department", cascade="all, delete-orphan")  # type: ignore[name-defined]
