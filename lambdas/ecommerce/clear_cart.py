from app.services.cart_service import CartService
from lambdas.ecommerce.cart_utils import get_user_id
from lambdas.handler import error, ok


def lambda_handler(event, context):
    user_id = get_user_id(event)
    if not user_id:
        return error("Missing user_id", status=400)

    return ok(CartService().clear_cart(user_id))
