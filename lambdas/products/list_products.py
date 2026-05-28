from app.services.product_service import ProductService
from lambdas.handler import ok, query_params


def lambda_handler(event, context):
    params = query_params(event)
    svc = ProductService()
    products = svc.list_products(
        category=params.get("category"),
        search=params.get("search") or params.get("q"),
        limit=params.get("limit") or 24,
        cursor=params.get("cursor"),
    )
    if not params:
        return ok(products.get("items", []))
    return ok(products)
