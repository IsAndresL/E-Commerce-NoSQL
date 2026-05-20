import json
from app.services.ecommerce_service import ECommerceService


def lambda_handler(event, context):
    user_id = None
    if event.get("pathParameters"):
        user_id = event["pathParameters"].get("user_id")
    user_id = user_id or event.get("user_id")

    service = ECommerceService()
    orders = service.get_recent_orders(user_id)
    return {"statusCode": 200, "body": json.dumps([o.model_dump() for o in orders])}
