from app.services.ecommerce_service import ECommerceService
from lambdas.handler import not_found, ok


def lambda_handler(event, context):
    user_id = None
    # API Gateway v2
    if event.get("pathParameters"):
        user_id = event["pathParameters"].get("user_id")
    # direct invoke
    user_id = user_id or event.get("user_id")

    service = ECommerceService()
    profile = service.get_user_profile(user_id)
    if not profile:
        return not_found("User profile not found")
    return ok(profile)
