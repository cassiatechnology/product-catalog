from __future__ import annotations
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship("Department", back_populates="categories")  # type: ignore[name-defined]
    
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category", cascade="all, delete-orphan")  # type: ignore[name-defined]
