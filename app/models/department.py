from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # PK already indexed
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Avoid duplicate department names
    __table_args__ = (
        UniqueConstraint("name", name="uq_departments_name"),
    )

    categories = relationship(
        "Category",
        back_populates="department",
        cascade="all, delete-orphan"
    )
