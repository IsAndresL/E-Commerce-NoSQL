import boto3

def create_ecommerce_table():
    """
    Create the 'ecommerce' table in DynamoDB with PK and SK as primary keys.
    """
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1", endpoint_url="http://dynamodb:8000")

    table_name = "ecommerce"
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
