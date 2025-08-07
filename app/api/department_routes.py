from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.schemas.department import DepartmentCreate, DepartmentRead
from app.models.department import Department
from sqlalchemy import select

router = APIRouter(prefix="/departments", tags=["Departments"])

async def get_db():
    """
    Dependency that provides a database session.
    """
    async with async_session() as session:
        yield session


@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_department(dept: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new department.

    - **name**: Name of the department (unique).
    """
    # Create a new Department instance from the request data
    new_dept = Department(**dept.model_dump())
    db.add(new_dept)

    await db.commit()
    await db.refresh(new_dept)

    return new_dept


@router.get("/", response_model=list[DepartmentRead])
async def list_departments(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all departments.

    Returns a list of all departments in the system.
    """
    # Select all departments from the database
    result = await db.execute(select(Department))
    
    return result.scalars().all()
