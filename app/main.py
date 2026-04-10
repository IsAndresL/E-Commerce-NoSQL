from fastapi import FastAPI
from app.api.routes import products, ecommerce

app = FastAPI(title="E-commerce API")

app.include_router(products.router, prefix="/products")
app.include_router(ecommerce.router, prefix="/ecommerce")
