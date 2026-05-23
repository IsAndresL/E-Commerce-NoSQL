from app.services.ecommerce_service import ECommerceService
from lambdas.handler import not_found, ok


def lambda_handler(event, context):
    order_id = None
    if event.get("pathParameters"):
        order_id = event["pathParameters"].get("order_id")
    order_id = order_id or event.get("order_id")

    service = ECommerceService()
    details = service.get_order_details(order_id)
    if not details:
        return not_found("Order details not found")
    return ok(details)
