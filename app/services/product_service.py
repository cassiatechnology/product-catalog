from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


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


async def update_product(db: AsyncSession, product_id: int, product_in: ProductUpdate) -> Product | None:
    product = await get_product_by_id(db, product_id)

    if not product:
        return None

    # Update only submitted fields
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    product = await get_product_by_id(db, product_id)

    if not product:
        return False
    
    await db.delete(product)
    await db.commit()
    
    return True