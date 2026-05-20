from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigatewayv2 as apigwv2
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from constructs import Construct
import os
from typing import Dict


class ApiStack(Stack):
    def __init__(self, scope: Construct, id: str, persistence_table=None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Package the whole project as the lambda asset so handlers can import `app.*` modules.
        project_root = os.getcwd()

        # Discover and create lambdas for ecommerce handlers
        handlers = {
            # path: module_name
            "/ecommerce/user/{user_id}/profile": "get_user_profile",
            "/ecommerce/user/{user_id}/orders": "get_recent_orders",
            "/ecommerce/order/{order_id}/details": "get_order_details",
            "/ecommerce/order/{order_id}/items": "get_order_items",
            "/ecommerce/user/{user_id}/order/{order_id}/details": "get_user_order_details",
            "/ecommerce/user/{user_id}/order/{order_id}/items": "get_user_order_items",
            "/ecommerce/dashboard-data": "dashboard_data",
        }

        lambda_map: Dict[str, _lambda.Function] = {}

        for path, module in handlers.items():
            fn = _lambda.Function(
                self,
                f"Ecommerce_{module}",
                runtime=_lambda.Runtime.PYTHON_3_11,
                handler=f"lambdas.ecommerce.{module}.lambda_handler",
                code=_lambda.Code.from_asset(project_root),
                environment={"TABLE_NAME": persistence_table.table_name if persistence_table else "ecommerce"},
            )
            if persistence_table:
                persistence_table.grant_read_write_data(fn)
            lambda_map[path] = fn

        # Products lambda (example)
        products_fn = _lambda.Function(
            self,
            "ProductsList",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambdas.products.list_products.lambda_handler",
            code=_lambda.Code.from_asset(project_root),
            environment={"TABLE_NAME": persistence_table.table_name if persistence_table else "ecommerce"},
        )
        if persistence_table:
            persistence_table.grant_read_write_data(products_fn)
        lambda_map["/products"] = products_fn

        # HTTP API (API Gateway v2 - HTTP API)
        http_api = apigwv2.HttpApi(self, "EcommerceHttpApi", api_name="EcommerceHttpApi")

        # Create integrations and routes
        for path, fn in lambda_map.items():
            integration = HttpLambdaIntegration(f"Integration_{fn.node.id}", fn)
            # Default to GET for these handlers
            http_api.add_routes(path=path, methods=[apigwv2.HttpMethod.GET], integration=integration)

