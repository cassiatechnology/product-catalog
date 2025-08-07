from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import create_product, get_product_by_id, list_products, update_product

router = APIRouter(prefix="/products", tags=["Products"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await create_product(db, product)

@router.get("/", response_model=List[ProductRead])
async def get_all_products(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await list_products(db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.put("/{product_id}", response_model=ProductRead)
async def update(product_id: int, product_in: ProductUpdate, db: AsyncSession = Depends(get_db)):
    product = await update_product(db, product_id, product_in)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product