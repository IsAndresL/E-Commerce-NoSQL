from app.services.dynamodb_adapter import DynamoDBAdapter
from boto3.dynamodb.conditions import Attr


class ProductRepository:
    def __init__(self, adapter: DynamoDBAdapter | None = None):
        self.adapter = adapter or DynamoDBAdapter()

    def list_products(self) -> list[dict]:
        return self.adapter.scan_items(
            Attr("PK").begins_with("PRODUCT#") & Attr("SK").eq("#METADATA")
        )

    def get_product(self, product_id: str) -> dict | None:
        return self.adapter.get_item({"PK": f"PRODUCT#{product_id}", "SK": "#METADATA"})