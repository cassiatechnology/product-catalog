from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, select
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
    product = Product(**product_in.model_dump())
    db.add(product)

    await db.commit()
    await db.refresh(product)

    return product


async def list_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "id",
    sort_order: str = "asc"
) -> list[Product]:
    query = select(Product)

    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)

    # Dinamic sorting
    sort_column = getattr(Product, sort_by, Product.id)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
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