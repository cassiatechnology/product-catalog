from sqlalchemy import Integer, String, Text, ForeignKey, Numeric, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # no index=True
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,  # no index=True
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_products_name"),
        Index("ix_products_name", "name"),
        Index("ix_products_price", "price"),
        Index("ix_products_category_id", "category_id"),
    )

    category = relationship("Category", back_populates="products")
