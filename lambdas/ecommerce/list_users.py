from app.services.ecommerce_service import ECommerceService
from lambdas.handler import ok


def lambda_handler(event, context):
    service = ECommerceService()
    users = service.list_users()
    return ok(users)