from pydantic import BaseModel, ConfigDict

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
