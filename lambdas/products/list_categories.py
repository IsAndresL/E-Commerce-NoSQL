from app.services.product_service import ProductService
from lambdas.handler import ok


def lambda_handler(event, context):
    return ok(ProductService().list_categories())
