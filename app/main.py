from fastapi import FastAPI
from app.api import product_routes
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="Product Catalog API")

app.include_router(product_routes.router)

# Create the database tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
