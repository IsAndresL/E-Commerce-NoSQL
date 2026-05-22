"""Deploy example Lambda functions to MiniStack (local AWS emulator).

Usage: python scripts/deploy_lambdas.py

Requirements: boto3
"""
import io
import zipfile
import os
import json
import boto3


MINISTACK_ENDPOINT = os.environ.get("MINISTACK_ENDPOINT", "http://localhost:4566")


def zip_lambda(handler_file_path):
    """Create a zip containing the handler file at root and the `app/` package."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    handler_file_path = os.path.abspath(handler_file_path)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # add app/ package
        app_dir = os.path.join(project_root, "app")
        for root, _, files in os.walk(app_dir):
            for f in files:
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, start=project_root)
                zf.write(full, arcname)
        # add handler file at zip root with its basename
        zf.write(handler_file_path, os.path.basename(handler_file_path))
    buf.seek(0)
    return buf.read()


def create_function(lambda_name, zip_bytes, handler_module_name):
    lam = boto3.client(
        "lambda",
        endpoint_url=MINISTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )

    role = "arn:aws:iam::000000000000:role/r"

    env_vars = {
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_ENDPOINT_URL": "http://ministack:4566",
        "ECOMMERCE_TABLE_NAME": "ecommerce",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379",
    }

    try:
        resp = lam.create_function(
            FunctionName=lambda_name,
            Runtime="python3.11",
            Role=role,
            Handler=f"{handler_module_name}.lambda_handler",
            Code={"ZipFile": zip_bytes},
            Publish=True,
            PackageType="Zip",
            Environment={"Variables": env_vars},
        )
        print(f"Created function {lambda_name}: {resp['FunctionArn']}")
    except lam.exceptions.ResourceConflictException:
        print(f"Function {lambda_name} already exists, updating code...")
        resp = lam.update_function_code(FunctionName=lambda_name, ZipFile=zip_bytes, Publish=True)
        # update configuration in case env changed
        lam.update_function_configuration(FunctionName=lambda_name, Environment={"Variables": env_vars})
        print(f"Updated function {lambda_name}: {resp.get('FunctionArn')}")


def main():
    base = os.path.join(os.path.dirname(__file__), "..", "lambdas")
    base = os.path.abspath(base)

    functions = [
        ("ecommerce_get_user_profile", os.path.join(base, "ecommerce", "get_user_profile.py")),
        ("ecommerce_get_recent_orders", os.path.join(base, "ecommerce", "get_recent_orders.py")),
        ("ecommerce_get_order_details", os.path.join(base, "ecommerce", "get_order_details.py")),
        ("ecommerce_get_order_items", os.path.join(base, "ecommerce", "get_order_items.py")),
        ("ecommerce_get_user_order_details", os.path.join(base, "ecommerce", "get_user_order_details.py")),
        ("ecommerce_get_user_order_items", os.path.join(base, "ecommerce", "get_user_order_items.py")),
        ("ecommerce_dashboard_data", os.path.join(base, "ecommerce", "dashboard_data.py")),
        ("products_list", os.path.join(base, "products", "list_products.py")),
    ]

    for name, handler_path in functions:
        print(f"Packing {name} from {handler_path}")
        zip_bytes = zip_lambda(handler_path)
        module_name = os.path.splitext(os.path.basename(handler_path))[0]
        create_function(name, zip_bytes, module_name)


if __name__ == "__main__":
    main()
