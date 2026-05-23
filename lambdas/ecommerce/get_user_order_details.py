from app.services.ecommerce_service import ECommerceService
from lambdas.handler import not_found, ok


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
        return not_found("Order not found for user")

    details = service.get_order_details(order_id)
    if not details:
        return not_found("Order details not found")
    return ok(details)
