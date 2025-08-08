from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import category_routes, department_routes, product_routes
from app.db.base import Base
from app.db.session import engine

import app.models  # noqa: F401

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Product Catalog API",
    lifespan=lifespan,
)

app.include_router(department_routes.router)
app.include_router(category_routes.router)
app.include_router(product_routes.router)
