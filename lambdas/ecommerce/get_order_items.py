from app.services.ecommerce_service import ECommerceService
from lambdas.handler import ok


def lambda_handler(event, context):
    order_id = None
    if event.get("pathParameters"):
        order_id = event["pathParameters"].get("order_id")
    order_id = order_id or event.get("order_id")

    service = ECommerceService()
    items = service.get_order_items(order_id)
    return ok(items)
