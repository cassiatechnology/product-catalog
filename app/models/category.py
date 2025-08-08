from sqlalchemy import Integer, String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # remove index=True
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,  # remove index=True
    )

    __table_args__ = (
        # Avoid the same category name duplicated within the same department
        UniqueConstraint("department_id", "name", name="uq_categories_department_name"),
        Index("ix_categories_department_id", "department_id"),
        Index("ix_categories_name", "name"),
    )

    department = relationship("Department", back_populates="categories")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
