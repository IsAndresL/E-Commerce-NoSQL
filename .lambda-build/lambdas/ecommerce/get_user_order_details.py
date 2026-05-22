import json
from app.services.ecommerce_service import ECommerceService


def lambda_handler(event, context):
    user_id = None
    order_id = None
    if event.get("pathParameters"):
        user_id = event["pathParameters"].get("user_id")
        order_id = event["pathParameters"].get("order_id")
    user_id = user_id or event.get("user_id")
    order_id = order_id or event.get("order_id")

    service = ECommerceService()
    if not service.user_has_order(user_id, order_id):
        return {"statusCode": 404, "body": json.dumps({"detail": "Order not found for user"}), "headers": {"Access-Control-Allow-Origin": "*"}}

    details = service.get_order_details(order_id)
    if not details:
        return {"statusCode": 404, "body": json.dumps({"detail": "Order details not found"}), "headers": {"Access-Control-Allow-Origin": "*"}}
    return {"statusCode": 200, "body": json.dumps(details.model_dump()), "headers": {"Access-Control-Allow-Origin": "*"}}
