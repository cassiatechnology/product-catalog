from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Register models so Base.metadata sees them
from app.models.department import Department  # noqa: F401
from app.models.category import Category      # noqa: F401
from app.models.product import Product        # noqa: F401
