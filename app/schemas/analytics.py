from pydantic import BaseModel, ConfigDict

class AvgPriceByDepartmentRead(BaseModel):
    department_id: int
    department_name: str
    avg_price: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"department_id": 1, "department_name": "Men", "avg_price": 104.95}
        }
    )


class TotalStockByCategoryRead(BaseModel):
    category_id: int
    category_name: str
    department_id: int
    department_name: str
    total_stock: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": 6,
                "category_name": "T-shirt",
                "department_id": 1,
                "department_name": "Men",
                "total_stock": 148,
            }
        }
    )


class CountProductsByDepartmentRead(BaseModel):
    department_id: int
    department_name: str
    product_count: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"department_id": 2, "department_name": "Women", "product_count": 10}
        }
    )


class TotalValueByDepartmentRead(BaseModel):
    department_id: int
    department_name: str
    total_value: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"department_id": 2, "department_name": "Women", "total_value": 15892.40}
        }
    )
