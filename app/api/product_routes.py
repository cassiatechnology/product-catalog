from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import (
    create_product,
    delete_product,
    get_product_by_id,
    list_products,
    update_product,
    get_product_with_relationships
)

router = APIRouter(prefix="/products", tags=["Products"])

async def get_db():
    """
    Dependency that provides a database session.
    """
    async with async_session() as session:
        yield session


@router.get("/by-category/{category_id}", response_model=List[ProductRead])
async def list_products_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all products belonging to a given category.

    - **category_id**: ID of the category to filter products by.
    """
    # Select all products that belong to a specific category
    result = await db.execute(
        select(Product)
        .where(Product.category_id == category_id)
        .options(
            selectinload(Product.category).selectinload(Category.department)
        )
    )

    return result.scalars().all()


@router.get("/by-department/{department_id}", response_model=List[ProductRead])
async def list_products_by_department(
    department_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all products belonging to a given department.

    - **department_id**: ID of the department to filter products by.
    """
    # Select all products whose category belongs to a specific department
    result = await db.execute(
        select(Product)
        .join(Product.category)
        .where(Category.department_id == department_id)
        .options(
            selectinload(Product.category).selectinload(Category.department)
        )
    )

    return result.scalars().all()


@router.get("/", response_model=List[ProductRead])
async def get_all_products(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    category_id: Optional[int] = None,
    department_id: Optional[int] = None,  # Added department filter
    db: AsyncSession = Depends(get_db)
):
    """
    List products with optional filters, sorting, and pagination.

    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **name**: Filter by product name (partial match)
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **sort_by**: Field to sort by (default: id)
    - **sort_order**: Sort direction ("asc" or "desc", default: asc)
    - **category_id**: Filter by category ID
    - **department_id**: Filter by department ID (new!)
    """
    # Forward all filters to the service layer
    return await list_products(
        db,
        skip=skip,
        limit=limit,
        name=name,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        category_id=category_id,
        department_id=department_id,  # Pass to service
    )


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a product by its ID.

    - **product_id**: ID of the product to retrieve.
    """
    product = await get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new product.

    - **name**: Product name (unique)
    - **description**: Product description (optional)
    - **price**: Product price
    - **stock**: Inventory stock
    - **category_id**: Category this product belongs to
    """
    new_product = await create_product(db, product)

    return await get_product_with_relationships(db, new_product.id)


@router.put("/{product_id}", response_model=ProductRead)
async def update(product_id: int, product_in: ProductUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update an existing product by its ID.

    - **product_id**: ID of the product to update.
    """
    product = await update_product(db, product_id, product_in)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return await get_product_with_relationships(db, product.id)


@router.delete("/{product_id}", status_code=204)
async def delete(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a product by its ID.

    - **product_id**: ID of the product to delete.
    """
    deleted = await delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Response(status_code=204)
