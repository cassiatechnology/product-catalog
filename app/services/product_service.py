from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Product
from app.schemas.product import ProductCreate

async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
    product = Product(**product_in.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

async def list_products(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[Product]:
    result = await db.execute(
        select(Product).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    return result.scalar_one_or_none()