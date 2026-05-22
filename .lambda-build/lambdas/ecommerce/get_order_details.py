import json
from app.services.ecommerce_service import ECommerceService


def lambda_handler(event, context):
    order_id = None
    if event.get("pathParameters"):
        order_id = event["pathParameters"].get("order_id")
    order_id = order_id or event.get("order_id")

    service = ECommerceService()
    details = service.get_order_details(order_id)
    if not details:
        return {"statusCode": 404, "body": json.dumps({"detail": "Order details not found"}), "headers": {"Access-Control-Allow-Origin": "*"}}
    return {"statusCode": 200, "body": json.dumps(details.model_dump()), "headers": {"Access-Control-Allow-Origin": "*"}}
