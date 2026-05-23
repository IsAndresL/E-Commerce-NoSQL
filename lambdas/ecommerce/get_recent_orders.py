from app.services.ecommerce_service import ECommerceService
from lambdas.handler import ok


def lambda_handler(event, context):
    user_id = None
    if event.get("pathParameters"):
        user_id = event["pathParameters"].get("user_id")
    user_id = user_id or event.get("user_id")

    service = ECommerceService()
    orders = service.get_recent_orders(user_id)
    return ok(orders)
