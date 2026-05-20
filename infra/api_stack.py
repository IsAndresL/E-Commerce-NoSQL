import os
from typing import Dict

from aws_cdk import Stack, aws_lambda as _lambda
from aws_cdk.aws_apigatewayv2_alpha import HttpApi, HttpMethod
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from constructs import Construct

_ASSET_EXCLUDE = [
    "cdk.out",
    ".git",
    "frontend",
    "deployer",
    "infra",
    "scripts",
    "data",
    "build",
    ".venv", "venv", "env",
    "__pycache__",
    "*.pyc",
    ".env",
    ".env.*",
    ".deployer-built",
    "*.md",
    "Makefile",
    "docker-compose.yml",
    "cdk.json",
]


class ApiStack(Stack):
    def __init__(self, scope: Construct, id: str, persistence_table=None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        project_root = os.getcwd()

        lambda_code = _lambda.Code.from_asset(project_root, exclude=_ASSET_EXCLUDE)

        base_env = {
            "TABLE_NAME": persistence_table.table_name if persistence_table else "ecommerce",
        }

        handlers = {
            "/ecommerce/user/{user_id}/profile":                  "get_user_profile",
            "/ecommerce/user/{user_id}/orders":                   "get_recent_orders",
            "/ecommerce/order/{order_id}/details":                "get_order_details",
            "/ecommerce/order/{order_id}/items":                  "get_order_items",
            "/ecommerce/user/{user_id}/order/{order_id}/details": "get_user_order_details",
            "/ecommerce/user/{user_id}/order/{order_id}/items":   "get_user_order_items",
            "/ecommerce/dashboard-data":                          "dashboard_data",
        }

        lambda_map: Dict[str, _lambda.Function] = {}

        for path, module in handlers.items():
            fn = _lambda.Function(
                self,
                f"Ecommerce_{module}",
                runtime=_lambda.Runtime.PYTHON_3_11,
                handler=f"lambdas.ecommerce.{module}.lambda_handler",
                code=lambda_code,
                environment=base_env,
            )
            if persistence_table:
                persistence_table.grant_read_write_data(fn)
            lambda_map[path] = fn

        products_fn = _lambda.Function(
            self,
            "ProductsList",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambdas.products.list_products.lambda_handler",
            code=lambda_code,
            environment=base_env,
        )
        if persistence_table:
            persistence_table.grant_read_write_data(products_fn)
        lambda_map["/products"] = products_fn

        http_api = HttpApi(self, "EcommerceHttpApi", api_name="EcommerceHttpApi")

        for path, fn in lambda_map.items():
            integration = HttpLambdaIntegration(f"Integration_{fn.node.id}", fn)
            http_api.add_routes(
                path=path,
                methods=[HttpMethod.GET],
                integration=integration,
            )