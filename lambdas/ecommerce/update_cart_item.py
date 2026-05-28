from pydantic import ValidationError

from app.models.cart import CartQuantityRequest
from app.services.cart_service import CartService
from lambdas.ecommerce.cart_utils import get_product_id, get_user_id, parse_body
from lambdas.handler import error, ok


def lambda_handler(event, context):
    user_id = get_user_id(event)
    product_id = get_product_id(event)
    if not user_id:
        return error("Missing user_id", status=400)
    if not product_id:
        return error("Missing product_id", status=400)

    try:
        payload = CartQuantityRequest.parse_obj(parse_body(event))
        cart = CartService().update_item(user_id, product_id, payload.quantity)
    except ValidationError as exc:
        return error(f"Invalid cart payload: {exc}", status=400)
    except ValueError as exc:
        return error(str(exc), status=400)

    return ok(cart)
