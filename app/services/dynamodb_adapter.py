import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

class DynamoDBAdapter:
    def __init__(self):
        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.table = self.dynamodb.Table("ecommerce")

    def get_item(self, key: dict):
        """
        Get a single item from the DynamoDB table.
        """
        try:
            response = self.table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            print(f"Error fetching item: {e}")
            return None

    def query_items(self, key_condition: dict, begins_with: str = None):
        """
        Query items from the DynamoDB table based on key condition and optional sort key prefix.
        """
        try:
            key_expression = f"{list(key_condition.keys())[0]} = :pk"
            expression_values = {":pk": key_condition[list(key_condition.keys())[0]]}

            if begins_with:
                key_expression += f" AND begins_with({list(key_condition.keys())[1]}, :sk)"
                expression_values[":sk"] = begins_with

            response = self.table.query(
                KeyConditionExpression=key_expression,
                ExpressionAttributeValues=expression_values,
            )
            return response.get("Items", [])
        except ClientError as e:
            print(f"Error querying items: {e}")
            return []
