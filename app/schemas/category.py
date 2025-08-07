from pydantic import BaseModel
from typing import Optional
from app.schemas.department import DepartmentRead

class CategoryBase(BaseModel):
    name: str
    department_id: int

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    department: Optional[DepartmentRead] = None

    class Config:
        from_attributes = True
