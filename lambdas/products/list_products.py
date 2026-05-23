from app.services.product_service import ProductService
from lambdas.handler import ok


def lambda_handler(event, context):
    svc = ProductService()
    products = svc.list_products()
    return ok(products)
