from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.schemas.product import ProductCreate, ProductRead
from app.services.product_service import create_product

router = APIRouter(prefix="/products", tags=["Products"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await create_product(db, product)
