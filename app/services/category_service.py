# app/services/category_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category

async def get_category_by_id(db: AsyncSession, category_id: int) -> Category | None:
    """
    Retrieve a Category by its ID (no relationships).
    """
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()
