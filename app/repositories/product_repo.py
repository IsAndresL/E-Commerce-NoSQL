from app.services.dynamodb_adapter import DynamoDBAdapter
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError


class ProductRepository:
    def __init__(self, adapter: DynamoDBAdapter | None = None):
        self.adapter = adapter or DynamoDBAdapter()

    def list_products(self) -> list[dict]:
        return self.adapter.scan_items(
            Attr("PK").begins_with("PRODUCT#") & Attr("SK").eq("#METADATA")
        )

    def get_product(self, product_id: str) -> dict | None:
        return self.adapter.get_item({"PK": f"PRODUCT#{product_id}", "SK": "#METADATA"})

    def reserve_stock(self, product_id: str, quantity: int) -> dict:
        if quantity <= 0:
            return self.get_product(product_id) or {}

        table = self.adapter.table
        try:
            response = table.update_item(
                Key={"PK": f"PRODUCT#{product_id}", "SK": "#METADATA"},
                UpdateExpression="SET stock = stock - :qty",
                ConditionExpression=Attr("stock").gte(quantity),
                ExpressionAttributeValues={":qty": quantity},
                ReturnValues="UPDATED_NEW",
            )
            return response.get("Attributes", {})
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code == "ConditionalCheckFailedException":
                raise ValueError(f"Stock insuficiente para {product_id}") from exc
            raise