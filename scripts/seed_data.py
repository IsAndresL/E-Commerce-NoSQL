import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings


def _dynamodb_resource():
    settings = get_settings()
    kwargs = {"region_name": settings.aws_region}

    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id

    if settings.aws_secret_access_key:
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    return boto3.resource("dynamodb", **kwargs), settings.ecommerce_table_name


def ensure_table_exists(dynamodb, table_name: str):
    try:
        table = dynamodb.Table(table_name)
        table.load()
        return table
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "ResourceNotFoundException":
            raise

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table


def seed_items(table):
    items = [
        {
            "PK": "USER#1",
            "SK": "PROFILE",
            "name": "Luisa",
            "email": "luisa@mercado.com",
            "addresses": ["Calle 10, Bogota", "Ave. 5, Medellin"],
            "payments": ["Visa ...1234", "PayPal"],
        },
        {
            "PK": "USER#1",
            "SK": "ORDER#202311151430",
            "id": "ORD#553",
            "status": "Pago exitoso",
            "created_at": "2023-11-15T14:30Z",
            "shipping_address": "Calle 10",
            "total": 540,
        },
        {
            "PK": "USER#1",
            "SK": "ORDER#202311010915",
            "id": "ORD#554",
            "status": "Enviado",
            "created_at": "2023-11-01T09:15Z",
            "shipping_address": "Calle 10",
            "total": 830,
        },
        {
            "PK": "USER#1",
            "SK": "ORDER#202310270800",
            "id": "ORD#555",
            "status": "Pago exitoso",
            "created_at": "2023-10-27T08:00Z",
            "shipping_address": "Calle 10",
            "total": 1250,
        },
        {
            "PK": "USER#1",
            "SK": "ORDER#202312021000",
            "id": "ORD#556",
            "status": "En preparacion",
            "created_at": "2023-12-02T10:00Z",
            "shipping_address": "Ave. 5, Medellin",
            "total": 320,
        },
        {
            "PK": "ORDER#555",
            "SK": "DETAILS",
            "order_id": "ORD#555",
            "date": "2023-10-27T08:00Z",
            "status": "Pago exitoso",
            "shipping_address": "Calle 10, Bogota",
            "total": 1250,
        },
        {
            "PK": "ORDER#555",
            "SK": "ITEM#1",
            "name": "Laptop XPS",
            "quantity": 1,
            "unit_price": 1200,
            "subtotal": 1200,
        },
        {
            "PK": "ORDER#555",
            "SK": "ITEM#2",
            "name": "Libro: El Capital",
            "quantity": 2,
            "unit_price": 25,
            "subtotal": 50,
        },
        {
            "PK": "ORDER#556",
            "SK": "DETAILS",
            "order_id": "ORD#556",
            "date": "2023-12-02T10:00Z",
            "status": "En preparacion",
            "shipping_address": "Ave. 5, Medellin",
            "total": 320,
        },
        {
            "PK": "ORDER#556",
            "SK": "ITEM#1",
            "name": "Mouse Inalambrico",
            "quantity": 1,
            "unit_price": 40,
            "subtotal": 40,
        },
        {
            "PK": "USER#2",
            "SK": "PROFILE",
            "name": "Carlos",
            "email": "carlos@mercado.com",
            "addresses": ["Cra 45, Cali"],
            "payments": ["Mastercard ...8899"],
        },
        {
            "PK": "USER#2",
            "SK": "ORDER#202312051830",
            "id": "ORD#900",
            "status": "Pago exitoso",
            "created_at": "2023-12-05T18:30Z",
            "shipping_address": "Cra 45, Cali",
            "total": 470,
        },
        {
            "PK": "ORDER#900",
            "SK": "DETAILS",
            "order_id": "ORD#900",
            "date": "2023-12-05T18:30Z",
            "status": "Pago exitoso",
            "shipping_address": "Cra 45, Cali",
            "total": 470,
        },
        {
            "PK": "ORDER#900",
            "SK": "ITEM#1",
            "name": "Teclado Mecanico",
            "quantity": 1,
            "unit_price": 470,
            "subtotal": 470,
        },
    ]

    with table.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as batch:
        for item in items:
            batch.put_item(Item=item)


if __name__ == "__main__":
    dynamodb, table_name = _dynamodb_resource()
    table = ensure_table_exists(dynamodb, table_name)
    seed_items(table)
    print(f"Seed completed in table: {table_name}")
