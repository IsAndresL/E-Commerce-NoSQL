import os

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.models.ecommerce import DashboardResponse, OrderDetails, OrderItem, OrderSummary, UserProfile
from app.services.ecommerce_dashboard_service import ECommerceDashboardService
from app.services.ecommerce_service import ECommerceService

router = APIRouter()

ecommerce_service = ECommerceService()
dashboard_service = ECommerceDashboardService(ecommerce_service)


@router.get("/user/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """
    Get user profile by user ID.
    """
    profile = ecommerce_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile


@router.get("/user/{user_id}/orders", response_model=list[OrderSummary])
async def get_recent_orders(user_id: str):
    """
    Get recent orders for a user.
    """
    orders = ecommerce_service.get_recent_orders(user_id)
    return orders


@router.get("/order/{order_id}/details", response_model=OrderDetails)
async def get_order_details(order_id: str):
    """
    Get order details by order ID.
    """
    order_details = ecommerce_service.get_order_details(order_id)
    if not order_details:
        raise HTTPException(status_code=404, detail="Order details not found")
    return order_details


@router.get("/order/{order_id}/items", response_model=list[OrderItem])
async def get_order_items(order_id: str):
    """
    Get items of an order by order ID.
    """
    items = ecommerce_service.get_order_items(order_id)
    return items


@router.get("/user/{user_id}/order/{order_id}/details", response_model=OrderDetails)
async def get_user_order_details(user_id: str, order_id: str):
    """
    Get order details only if the order belongs to the user.
    """
    if not ecommerce_service.user_has_order(user_id, order_id):
        raise HTTPException(status_code=404, detail="Order not found for user")

    order_details = ecommerce_service.get_order_details(order_id)
    if not order_details:
        raise HTTPException(status_code=404, detail="Order details not found")
    return order_details


@router.get("/user/{user_id}/order/{order_id}/items", response_model=list[OrderItem])
async def get_user_order_items(user_id: str, order_id: str):
    """
    Get order items only if the order belongs to the user.
    """
    if not ecommerce_service.user_has_order(user_id, order_id):
        raise HTTPException(status_code=404, detail="Order not found for user")

    return ecommerce_service.get_order_items(order_id)


@router.get("/dashboard-data", response_model=DashboardResponse)
async def dashboard_data(
    user_id: str = Query(default="1"),
    order_id: str = Query(default="555"),
):
    return dashboard_service.build_dashboard(user_id=user_id, order_id=order_id)


@router.get("/dashboard", include_in_schema=False)
async def dashboard():
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return RedirectResponse(url=frontend_url)
