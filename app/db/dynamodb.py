import boto3
from app.core.config import get_settings


settings = get_settings()

dynamodb_kwargs = {"region_name": settings.aws_region}

if settings.aws_access_key_id:
    dynamodb_kwargs["aws_access_key_id"] = settings.aws_access_key_id

if settings.aws_secret_access_key:
    dynamodb_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

if settings.dynamodb_endpoint_url:
    dynamodb_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

dynamodb = boto3.resource("dynamodb", **dynamodb_kwargs)


def get_table(table_name: str | None = None):
    return dynamodb.Table(table_name or settings.ecommerce_table_name)