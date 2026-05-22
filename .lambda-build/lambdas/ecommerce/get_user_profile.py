import json
from app.services.ecommerce_service import ECommerceService


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
        return {"statusCode": 404, "body": json.dumps({"detail": "User profile not found"}), "headers": {"Access-Control-Allow-Origin": "*"}}
    return {"statusCode": 200, "body": json.dumps(profile.model_dump()), "headers": {"Access-Control-Allow-Origin": "*"}}
