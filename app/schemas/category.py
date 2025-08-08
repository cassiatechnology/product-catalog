from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
