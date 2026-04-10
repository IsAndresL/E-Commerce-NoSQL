import boto3

def test_connection():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1", endpoint_url="http://dynamodb:8000")
    try:
        tables = dynamodb.meta.client.list_tables()["TableNames"]
        print(f"Connected to DynamoDB. Tables: {tables}")
    except Exception as e:
        print(f"Error connecting to DynamoDB: {e}")

if __name__ == "__main__":
    test_connection()
