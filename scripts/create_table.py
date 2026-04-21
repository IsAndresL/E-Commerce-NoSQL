import boto3

from app.core.config import get_settings

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

    if settings.dynamodb_endpoint_url:
        dynamodb_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    dynamodb = boto3.resource("dynamodb", **dynamodb_kwargs)

    table_name = settings.ecommerce_table_name
    existing_tables = dynamodb.meta.client.list_tables()["TableNames"]

    if table_name in existing_tables:
        print(f"Table '{table_name}' already exists.")
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
        ],
        BillingMode="PAY_PER_REQUEST",  # Modo de facturación
    )

    table.wait_until_exists()
    print(f"Table '{table_name}' created successfully.")

if __name__ == "__main__":
    create_ecommerce_table()
