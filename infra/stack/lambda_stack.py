import os
from typing import cast
from typing import Dict

from aws_cdk import BundlingOptions, Duration, Stack, aws_dynamodb as dynamodb, aws_lambda as _lambda, CfnOutput
from aws_cdk import aws_apigatewayv2 as apigwv2
from aws_cdk import aws_apigatewayv2_integrations as apigwv2_integrations
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
	".infra_venv",
	"venv", "env",
	".venv",
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


class LambdaStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        dynamo_table: dynamodb.Table,
        redis_host: str,
        redis_port: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        project_root = os.getcwd()
        lambda_code = _lambda.Code.from_asset(
            project_root,
            exclude=_ASSET_EXCLUDE,
            bundling=BundlingOptions(
                image=_lambda.Runtime.PYTHON_3_11.bundling_image,
                command=[
                    "sh",
                    "-lc",
                    "PIP_ROOT_USER_ACTION=ignore PIP_DISABLE_PIP_VERSION_CHECK=1 python -m pip install --no-cache-dir -r /asset-input/requirements.txt -t /asset-output && cp -au /asset-input/app /asset-output/app && cp -au /asset-input/lambdas /asset-output/lambdas && cp -au /asset-input/requirements.txt /asset-output/requirements.txt",
                ],
            ),
        )

        shared_env = {
            "TABLE_NAME": dynamo_table.table_name,
            "ECOMMERCE_TABLE_NAME": dynamo_table.table_name,
            "AWS_ENDPOINT_URL": "http://ministack:4566",
            "REDIS_HOST": redis_host,
            "REDIS_PORT": redis_port,
            "REDIS_DB": "0",
            "REDIS_CACHE_TTL_SECONDS": "120",
        }

        handlers = {
            "/ecommerce/users": "list_users",
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
                code=lambda_code,
                environment=shared_env,
                timeout=Duration.seconds(10),
            )
            dynamo_table.grant_read_write_data(fn)
            lambda_map[path] = fn

        products_fn = _lambda.Function(
            self,
            "ProductsList",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambdas.products.list_products.lambda_handler",
            code=lambda_code,
            environment=shared_env,
            timeout=Duration.seconds(10),
        )
        dynamo_table.grant_read_write_data(products_fn)
        lambda_map["/products"] = products_fn

        # Enable CORS for the frontend (allow all origins for local dev)
        http_api = apigwv2.HttpApi(
            self,
            "EcommerceHttpApi",
            api_name="EcommerceHttpApi",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=["http://localhost:5173"],
                allow_methods=[apigwv2.CorsHttpMethod.GET, apigwv2.CorsHttpMethod.OPTIONS],
                allow_headers=["*"],
            ),
        )

        for path, fn in lambda_map.items():
            integration = apigwv2_integrations.HttpLambdaIntegration(
                f"Integration_{fn.node.id}",
                cast(_lambda.IFunction, fn),
            )
            http_api.add_routes(
                path=path,
                methods=[apigwv2.HttpMethod.GET],
                integration=integration,
            )

        # Expose API URL and API id as CloudFormation outputs so deploy tooling can pick them up
        CfnOutput(self, "ApiUrl", value=http_api.url or "")
        CfnOutput(self, "ApiId", value=http_api.api_id)