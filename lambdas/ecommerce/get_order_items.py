import json
from app.services.ecommerce_service import ECommerceService


def lambda_handler(event, context):
    order_id = None
    if event.get("pathParameters"):
        order_id = event["pathParameters"].get("order_id")
    order_id = order_id or event.get("order_id")

    service = ECommerceService()
    items = service.get_order_items(order_id)
    return {"statusCode": 200, "body": json.dumps([i.model_dump() for i in items])}
