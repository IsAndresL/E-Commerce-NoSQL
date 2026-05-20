import json
from app.services.product_service import ProductService


def lambda_handler(event, context):
    svc = ProductService()
    products = svc.list_products()
    return {"statusCode": 200, "body": json.dumps(products)}
