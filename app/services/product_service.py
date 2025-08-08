from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import selectinload
from app.core.cache import cache, make_key
from app.models.category import Category
from app.models.department import Department
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

# Namespaces for cache
NS_PRODUCTS_LIST = "products:list"
NS_PRODUCTS_SUMMARY = "products:summary"

# TTLs (seconds)
TTL_LIST = 60
TTL_SUMMARY = 120


async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
    """
    Create and persist a new product in the database.
    """
    product = Product(**product_in.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)

    # Invalidate read caches after write
    await cache.invalidate_prefix(NS_PRODUCTS_LIST)
    await cache.invalidate_prefix(NS_PRODUCTS_SUMMARY)

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

    # Try cache first
    key = make_key(
        NS_PRODUCTS_LIST,
        skip=skip, limit=limit, name=name, min_price=min_price, max_price=max_price,
        sort_by=sort_by, sort_order=sort_order, category_id=category_id, department_id=department_id,
    )
    cached = await cache.get(key)
    
    if cached is not None:
        return cached

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

    items = result.scalars().all()

    # Save to cache
    await cache.set(key, items, TTL_LIST)

    return items


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    """
    Retrieve a product by its ID (without relationships).
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
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

    # Invalidate read caches after write
    await cache.invalidate_prefix(NS_PRODUCTS_LIST)
    await cache.invalidate_prefix(NS_PRODUCTS_SUMMARY)

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
    
    # Invalidate read caches after write
    await cache.invalidate_prefix(NS_PRODUCTS_LIST)
    await cache.invalidate_prefix(NS_PRODUCTS_SUMMARY)

    return True


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


async def avg_price_by_department(db: AsyncSession) -> list[dict]:
    """
    Aggregate: average product price per department.
    Returns: [{"department_id": int, "department_name": str, "avg_price": float}, ...]
    """
    key = make_key(NS_PRODUCTS_SUMMARY, name="avg_price_by_department")
    cached = await cache.get(key)

    if cached is not None:
        return cached

    query = (
        select(
            Department.id.label("department_id"),
            Department.name.label("department_name"),
            func.avg(Product.price).label("avg_price"),
        )
        .join(Category, Category.department_id == Department.id)
        .join(Product, Product.category_id == Category.id)
        .group_by(Department.id, Department.name)
        .order_by(Department.id)
    )

    rows = (await db.execute(query)).all()
    data = [dict(r._mapping) for r in rows]

    await cache.set(key, data, TTL_SUMMARY)

    return data


async def total_stock_by_category(db: AsyncSession) -> list[dict]:
    """
    Aggregate: total stock per category (with department for context).
    Returns: [{"category_id": int, "category_name": str, "department_id": int, "department_name": str, "total_stock": int}, ...]
    """
    key = make_key(NS_PRODUCTS_SUMMARY, name="total_stock_by_category")
    cached = await cache.get(key)

    if cached is not None:
        return cached

    query = (
        select(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            Department.id.label("department_id"),
            Department.name.label("department_name"),
            func.coalesce(func.sum(Product.stock), 0).label("total_stock"),
        )
        .join(Department, Category.department_id == Department.id)
        .join(Product, Product.category_id == Category.id)
        .group_by(Category.id, Category.name, Department.id, Department.name)
        .order_by(Department.id, Category.id)
    )

    rows = (await db.execute(query)).all()
    data = [dict(r._mapping) for r in rows]

    await cache.set(key, data, TTL_SUMMARY)

    return data


async def count_products_by_department(db: AsyncSession) -> list[dict]:
    """
    Aggregate: product count per department.
    Returns: [{"department_id": int, "department_name": str, "product_count": int}, ...]
    """
    key = make_key(NS_PRODUCTS_SUMMARY, name="count_products_by_department")
    cached = await cache.get(key)

    if cached is not None:
        return cached

    query = (
        select(
            Department.id.label("department_id"),
            Department.name.label("department_name"),
            func.count(Product.id).label("product_count"),
        )
        .join(Category, Category.department_id == Department.id)
        .join(Product, Product.category_id == Category.id)
        .group_by(Department.id, Department.name)
        .order_by(Department.id)
    )

    rows = (await db.execute(query)).all()
    data = [dict(r._mapping) for r in rows]

    await cache.set(key, data, TTL_SUMMARY)

    return data


async def total_value_by_department(db: AsyncSession) -> list[dict]:
    """
    Aggregate: total inventory value per department (sum of price * stock).
    Returns: [{"department_id": int, "department_name": str, "total_value": float}, ...]
    """
    key = make_key(NS_PRODUCTS_SUMMARY, name="total_value_by_department")
    cached = await cache.get(key)

    if cached is not None:
        return cached

    query = (
        select(
            Department.id.label("department_id"),
            Department.name.label("department_name"),
            func.coalesce(func.sum(Product.price * Product.stock), 0).label("total_value"),
        )
        .join(Category, Category.department_id == Department.id)
        .join(Product, Product.category_id == Category.id)
        .group_by(Department.id, Department.name)
        .order_by(Department.id)
    )

    rows = (await db.execute(query)).all()
    data = [dict(r._mapping) for r in rows]

    await cache.set(key, data, TTL_SUMMARY)

    return data
