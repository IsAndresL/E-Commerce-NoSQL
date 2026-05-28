import sys
import os
import time
from pathlib import Path
from typing import Any

import boto3

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings

def ensure_catalog_index(table):
    table.load()
    indexes = table.global_secondary_indexes or []
    existing = next((index for index in indexes if index.get("IndexName") == "GSI1"), None)
    if existing:
        wait_for_catalog_index(table)
        print("Catalog index 'GSI1' already exists.")
        return

    print("Creating catalog index 'GSI1'...")
    table.update(
        AttributeDefinitions=[
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexUpdates=[
            {
                "Create": {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            }
        ],
    )
    wait_for_catalog_index(table)
    print("Catalog index 'GSI1' created.")


def wait_for_catalog_index(table):
    for _ in range(60):
        table.reload()
        indexes = table.global_secondary_indexes or []
        index = next((item for item in indexes if item.get("IndexName") == "GSI1"), None)
        if index and index.get("IndexStatus") == "ACTIVE":
            return
        time.sleep(2)

def create_ecommerce_table():
    """
    Create the 'ecommerce' table in DynamoDB with PK and SK as primary keys.
    """
    settings = get_settings()

    dynamodb_kwargs = {"region_name": settings.aws_region}

    if settings.aws_access_key_id:
        dynamodb_kwargs["aws_access_key_id"] = settings.aws_access_key_id

    if settings.aws_secret_access_key:
        dynamodb_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

    # Allow overriding endpoint via AWS_ENDPOINT_URL env var (MiniStack gateway)
    endpoint_override = os.environ.get("AWS_ENDPOINT_URL") or os.environ.get("AWS_ENDPOINT")
    if endpoint_override:
        dynamodb_kwargs["endpoint_url"] = endpoint_override
    elif settings.dynamodb_endpoint_url:
        dynamodb_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    dynamodb: Any = boto3.resource("dynamodb", **dynamodb_kwargs)

    table_name = settings.ecommerce_table_name
    existing_tables = dynamodb.meta.client.list_tables()["TableNames"]

    if table_name in existing_tables:
        print(f"Table '{table_name}' already exists.")
        ensure_catalog_index(dynamodb.Table(table_name))
        return

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},  # Partition key
            {"AttributeName": "SK", "KeyType": "RANGE"},  # Sort key
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",  # Modo de facturación
    )

    table.wait_until_exists()
    ensure_catalog_index(table)
    print(f"Table '{table_name}' created successfully.")

if __name__ == "__main__":
    create_ecommerce_table()
