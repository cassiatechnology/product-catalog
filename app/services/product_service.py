from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import selectinload
from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
    """
    Create and persist a new product in the database.
    """
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
    sort_order: str = "asc",
    category_id: Optional[int] = None,
    department_id: Optional[int] = None,
) -> list[Product]:
    """
    List products with optional filters, sorting, and pagination.

    Filters supported:
    - name: partial match
    - min_price, max_price: price range
    - category_id: filter by category
    - department_id: filter by department (via JOIN on Category)
    Sorting supported by any product column.
    """

    # Always eager-load related category and department for proper serialization
    query = select(Product).options(
        selectinload(Product.category).selectinload(Category.department)
    )

    # Apply filters
    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    if category_id is not None:
        query = query.where(Product.category_id == category_id)
        
    if department_id is not None:
        # Join with Category to filter by department
        query = query.join(Product.category).where(Category.department_id == department_id)

    # Dynamic sorting
    sort_column = getattr(Product, sort_by, Product.id)
    query = query.order_by(desc(sort_column) if sort_order == "desc" else asc(sort_column))

    # Pagination
    query = query.offset(skip).limit(limit)

    # Execute query and return results
    result = await db.execute(query)

    return result.scalars().all()


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    """
    Retrieve a product by its ID (without relationships).
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )

    return result.scalar_one_or_none()


async def get_product_with_relationships(db: AsyncSession, product_id: int) -> Product | None:
    """
    Retrieve a product by its ID with category and department relationships loaded.
    """
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.category).selectinload(Category.department))
    )

    return result.scalar_one_or_none()


async def update_product(db: AsyncSession, product_id: int, product_in: ProductUpdate) -> Product | None:
    """
    Update a product by its ID.
    Only the fields provided in the update request will be modified.
    """
    product = await get_product_by_id(db, product_id)
    if not product:
        return None

    # Update only the fields sent in the request (partial update)
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product

async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """
    Delete a product by its ID.
    Returns True if the product was deleted, False if not found.
    """
    product = await get_product_by_id(db, product_id)
    if not product:
        return False

    await db.delete(product)
    await db.commit()
    
    return True
