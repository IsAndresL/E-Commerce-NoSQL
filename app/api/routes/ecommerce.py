from fastapi import APIRouter, HTTPException
from app.services.dynamodb_adapter import DynamoDBAdapter

router = APIRouter()

# Initialize the DynamoDB adapter
db_adapter = DynamoDBAdapter()

@router.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    Get user profile by user ID.
    """
    key = {"PK": f"USER#{user_id}", "SK": "PROFILE"}
    profile = db_adapter.get_item(key)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile

@router.get("/user/{user_id}/orders")
async def get_recent_orders(user_id: str):
    """
    Get recent orders for a user.
    """
    key_condition = {"PK": f"USER#{user_id}"}
    orders = db_adapter.query_items(key_condition, begins_with="ORDER#")
    return orders

@router.get("/order/{order_id}/details")
async def get_order_details(order_id: str):
    """
    Get order details by order ID.
    """
    key = {"PK": f"ORDER#{order_id}", "SK": "DETAILS"}
    order_details = db_adapter.get_item(key)
    if not order_details:
        raise HTTPException(status_code=404, detail="Order details not found")
    return order_details

@router.get("/order/{order_id}/items")
async def get_order_items(order_id: str):
    """
    Get items of an order by order ID.
    """
    key_condition = {"PK": f"ORDER#{order_id}"}
    items = db_adapter.query_items(key_condition, begins_with="ITEM#")
    return items
