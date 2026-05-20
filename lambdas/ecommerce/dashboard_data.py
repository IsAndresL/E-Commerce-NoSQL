import json
from app.services.ecommerce_dashboard_service import ECommerceDashboardService
from app.services.ecommerce_service import ECommerceService


def lambda_handler(event, context):
    # query parameters from API Gateway v2
    qs = event.get("queryStringParameters") or {}
    user_id = qs.get("user_id") or event.get("user_id")
    order_id = qs.get("order_id") or event.get("order_id")

    svc = ECommerceDashboardService(ECommerceService())
    # dashboard service has async method; use build_dashboard (sync) for Lambda
    dashboard = svc.build_dashboard(user_id, order_id)
    return {"statusCode": 200, "body": json.dumps(dashboard.model_dump())}
