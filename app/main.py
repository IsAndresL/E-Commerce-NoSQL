from fastapi import FastAPI
from app.api.routes import products

app = FastAPI(title="E-commerce API")

app.include_router(products.router, prefix="/products")
