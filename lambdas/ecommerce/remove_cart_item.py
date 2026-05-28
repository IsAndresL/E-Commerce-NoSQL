from app.services.cart_service import CartService
from lambdas.ecommerce.cart_utils import get_product_id, get_user_id
from lambdas.handler import error, ok


def lambda_handler(event, context):
    user_id = get_user_id(event)
    product_id = get_product_id(event)
    if not user_id:
        return error("Missing user_id", status=400)
    if not product_id:
        return error("Missing product_id", status=400)

    return ok(CartService().remove_item(user_id, product_id))
