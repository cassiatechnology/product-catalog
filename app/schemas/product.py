from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.schemas.category import CategoryRead

class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float
    stock: int = 0

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Stock must be non-negative")
        return v

class ProductCreate(ProductBase):
    category_id: int

class ProductRead(ProductBase):
    id: int
    category: Optional[CategoryRead] = None

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
