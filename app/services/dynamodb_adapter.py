import boto3
from botocore.exceptions import BotoCoreError, ClientError
from boto3.dynamodb.conditions import Key

from app.core.config import get_settings
from app.db.dynamodb import get_table


class DynamoDBAdapter:
    def __init__(self, table_name: str | None = None):
        settings = get_settings()
        self.table_name = table_name or settings.ecommerce_table_name
        self.table = get_table(self.table_name)

    def get_item(self, key: dict):
        """
        Get a single item from the DynamoDB table.
        """
        try:
            response = self.table.get_item(Key=key)
            return response.get("Item")
        except (ClientError, BotoCoreError) as e:
            print(f"Error fetching item: {e}")
            return None

    def query_items(
        self,
        partition_key_name: str,
        partition_key_value: str,
        sort_key_name: str | None = None,
        begins_with: str | None = None,
    ):
        """
        Query items from the DynamoDB table using DynamoDB key expressions.
        """
        try:
            key_condition = Key(partition_key_name).eq(partition_key_value)

            if sort_key_name and begins_with is not None:
                key_condition = key_condition & Key(sort_key_name).begins_with(begins_with)

            response = self.table.query(
                KeyConditionExpression=key_condition,
            )
            return response.get("Items", [])
        except (ClientError, BotoCoreError) as e:
            print(f"Error querying items: {e}")
            return []

    def put_item(self, item: dict):
        """
        Store an item in the DynamoDB table.
        """
        try:
            self.table.put_item(Item=item)
            return item
        except (ClientError, BotoCoreError) as e:
            print(f"Error storing item: {e}")
            return None
