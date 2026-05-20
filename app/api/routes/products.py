from fastapi import APIRouter
from app.services import product_service

router = APIRouter()

@router.get("/")
async def get_products():
    return product_service.list_products()