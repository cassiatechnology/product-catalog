from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.models.category import Category
from app.models.product import Product
from app.schemas.analytics import AvgPriceByDepartmentRead, CountProductsByDepartmentRead, TotalStockByCategoryRead, TotalValueByDepartmentRead
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.category_service import get_category_by_id
from app.services.product_service import (
    avg_price_by_department,
    count_products_by_department,
    create_product,
    delete_product,
    list_products,
    total_stock_by_category,
    total_value_by_department,
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

    ### Example
    **Request**
    ```
    GET /products/by-category/1
    ```

    **Response**
    ```json
    [
      {
        "id": 10,
        "name": "Silk Pink Blouse",
        "description": "Women's silk blouse, pink color, long sleeves.",
        "price": 129.9,
        "stock": 15,
        "category": {
          "id": 1,
          "name": "Blouse",
          "department_id": 2,
          "department": {"id": 2, "name": "Women"}
        }
      }
    ]
    ```
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

    ### Example
    **Request**
    ```
    GET /products/by-department/2
    ```

    **Response**
    ```json
    [
      {
        "id": 11,
        "name": "Summer Dress",
        "description": "Light floral summer dress, sleeveless.",
        "price": 149.9,
        "stock": 13,
        "category": {
          "id": 3,
          "name": "Dress",
          "department_id": 2,
          "department": {"id": 2, "name": "Women"}
        }
      }
    ]
    ```
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


@router.get("")
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

    ### Examples
    **Request**
    ```
    GET /products?skip=0&limit=10&name=dress&min_price=100&max_price=200&sort_by=price&sort_order=desc
    ```

    **Response (partial)**
    ```json
    [
      {
        "id": 12,
        "name": "Evening Dress",
        "description": "Elegant red evening dress, long.",
        "price": 299.9,
        "stock": 7,
        "category": {
          "id": 3,
          "name": "Dress",
          "department_id": 2,
          "department": {"id": 2, "name": "Women"}
        }
      }
    ]
    ```
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

    ### Example
    **Request**
    ```
    GET /products/10
    ```

    **Response**
    ```json
    {
      "id": 10,
      "name": "Silk Pink Blouse",
      "description": "Women's silk blouse, pink color, long sleeves.",
      "price": 129.9,
      "stock": 15,
      "category": {
        "id": 1,
        "name": "Blouse",
        "department_id": 2,
        "department": {"id": 2, "name": "Women"}
      }
    }
    ```
    """
    product = await get_product_with_relationships(db, product_id)

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

    ### Example
    **Request Body**
    ```json
    {
      "name": "Silk Pink Blouse",
      "description": "Women's silk blouse, pink color, long sleeves.",
      "price": 129.9,
      "stock": 15,
      "category_id": 1
    }
    ```

    **Response**
    ```json
    {
      "id": 10,
      "name": "Silk Pink Blouse",
      "description": "Women's silk blouse, pink color, long sleeves.",
      "price": 129.9,
      "stock": 15,
      "category": {
        "id": 1,
        "name": "Blouse",
        "department_id": 2,
        "department": {"id": 2, "name": "Women"}
      }
    }
    ```
    """
    # Validate category existence before persisting
    category = await get_category_by_id(db, product.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category_id: category not found")

    new_product = await create_product(db, product)
    # Return with relationships eagerly loaded to avoid async lazy loading issues
    return await get_product_with_relationships(db, new_product.id)


@router.put("/{product_id}", response_model=ProductRead)
async def update(product_id: int, product_in: ProductUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update an existing product by its ID.

    - **product_id**: ID of the product to update.

    ### Example
    **Request**
    ```
    PUT /products/10
    ```

    **Request Body**
    ```json
    {
      "price": 119.9,
      "stock": 18
    }
    ```

    **Response**
    ```json
    {
      "id": 10,
      "name": "Silk Pink Blouse",
      "description": "Women's silk blouse, pink color, long sleeves.",
      "price": 119.9,
      "stock": 18,
      "category": {
        "id": 1,
        "name": "Blouse",
        "department_id": 2,
        "department": {"id": 2, "name": "Women"}
      }
    }
    ```
    """
    # If changing the category, validate it first
    if product_in.category_id is not None:
        category = await get_category_by_id(db, product_in.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id: category not found")

    product = await update_product(db, product_id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Return with relationships eagerly loaded
    return await get_product_with_relationships(db, product.id)


@router.delete("/{product_id}", status_code=204)
async def delete(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a product by its ID.

    - **product_id**: ID of the product to delete.

    ### Example
    **Request**
    ```
    DELETE /products/10
    ```

    **Response**
    - 204 No Content
    """
    deleted = await delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return Response(status_code=204)


@router.get(
    "/summary/avg-price-by-department",
    response_model=List[AvgPriceByDepartmentRead],
    responses={
        200: {
            "description": "Average product price per department",
            "content": {
                "application/json": {
                    "examples": {
                        "sample": {
                            "summary": "Example list",
                            "value": [
                                {"department_id": 1, "department_name": "Men", "avg_price": 104.95},
                                {"department_id": 2, "department_name": "Women", "avg_price": 147.43}
                            ],
                        }
                    }
                }
            },
        }
    },
)
async def summary_avg_price_by_department(db: AsyncSession = Depends(get_db)):
    """
    Aggregation: average product price per department.
    """
    return await avg_price_by_department(db)


@router.get(
    "/summary/total-stock-by-category",
    response_model=List[TotalStockByCategoryRead],
    responses={
        200: {
            "description": "Total stock per category, with department context",
            "content": {
                "application/json": {
                    "examples": {
                        "sample": {
                            "summary": "Example list",
                            "value": [
                                {"category_id": 1, "category_name": "Blouse",  "department_id": 2, "department_name": "Women", "total_stock": 85},
                                {"category_id": 2, "category_name": "Pants",   "department_id": 2, "department_name": "Women", "total_stock": 60},
                                {"category_id": 3, "category_name": "Dress",   "department_id": 2, "department_name": "Women", "total_stock": 54},
                                {"category_id": 4, "category_name": "Pants",   "department_id": 1, "department_name": "Men",   "total_stock": 51},
                                {"category_id": 5, "category_name": "Shirt",   "department_id": 1, "department_name": "Men",   "total_stock": 55},
                                {"category_id": 6, "category_name": "T-shirt", "department_id": 1, "department_name": "Men",   "total_stock": 148}
                            ],
                        }
                    }
                }
            },
        }
    },
)
async def summary_total_stock_by_category(db: AsyncSession = Depends(get_db)):
    """
    Aggregation: total stock per category (with department context).
    """
    return await total_stock_by_category(db)


@router.get(
    "/summary/count-by-department",
    response_model=List[CountProductsByDepartmentRead],
    responses={
        200: {
            "description": "Product count per department",
            "content": {
                "application/json": {
                    "examples": {
                        "sample": {
                            "summary": "Example list",
                            "value": [
                                {"department_id": 1, "department_name": "Men",   "product_count": 10},
                                {"department_id": 2, "department_name": "Women", "product_count": 10}
                            ],
                        }
                    }
                }
            },
        }
    },
)
async def summary_count_by_department(db: AsyncSession = Depends(get_db)):
    """
    Aggregation: product count per department.
    """
    return await count_products_by_department(db)


@router.get(
    "/summary/total-value-by-department",
    response_model=List[TotalValueByDepartmentRead],
    responses={
        200: {
            "description": "Total inventory value per department (sum of price * stock)",
            "content": {
                "application/json": {
                    "examples": {
                        "sample": {
                            "summary": "Example list",
                            "value": [
                                {"department_id": 1, "department_name": "Men",   "total_value": 11234.10},
                                {"department_id": 2, "department_name": "Women", "total_value": 15892.40}
                            ],
                        }
                    }
                }
            },
        }
    },
)
async def summary_total_value_by_department(db: AsyncSession = Depends(get_db)):
    """
    Aggregation: total inventory value per department (sum of price * stock).
    """
    return await total_value_by_department(db)

    