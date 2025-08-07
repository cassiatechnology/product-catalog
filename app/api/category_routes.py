from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import async_session
from app.schemas.category import CategoryCreate, CategoryRead
from app.models.category import Category

router = APIRouter(prefix="/categories", tags=["Categories"])

async def get_db():
    """
    Dependency that provides a database session.
    """
    async with async_session() as session:
        yield session


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new category.

    - **name**: Name of the category.
    - **department_id**: ID of the department this category belongs to.
    """
    # Create a new Category instance from the request data
    new_category = Category(**category.model_dump())
    db.add(new_category)

    await db.commit()
    await db.refresh(new_category)

    # Reload with relationship eagerly loaded for correct serialization
    result = await db.execute(
        select(Category)
        .where(Category.id == new_category.id)
        .options(selectinload(Category.department))
    )
    new_category_with_dep = result.scalar_one()

    return new_category_with_dep


@router.get("/", response_model=list[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all categories.

    Returns a list of all categories in the system.
    """
    result = await db.execute(
        select(Category).options(selectinload(Category.department))
    )

    return result.scalars().all()


@router.get("/by-department/{department_id}", response_model=list[CategoryRead])
async def list_categories_by_department(
    department_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all categories for a specific department.

    - **department_id**: The ID of the department to filter categories by.
    """
    result = await db.execute(
        select(Category)
        .where(Category.department_id == department_id)
        .options(selectinload(Category.department))
    )

    return result.scalars().all()
