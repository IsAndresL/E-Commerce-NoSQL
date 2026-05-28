from app.services.dynamodb_adapter import DynamoDBAdapter
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError


class ProductRepository:
    CATALOG_INDEX = "GSI1"

    def __init__(self, adapter: DynamoDBAdapter | None = None):
        self.adapter = adapter or DynamoDBAdapter()

    def list_products(self) -> list[dict]:
        return self.adapter.query_items(
            "GSI1PK",
            "CATALOG#ALL",
            index_name=self.CATALOG_INDEX,
        )

    def list_products_page(
        self,
        category: str | None = None,
        limit: int = 24,
        cursor: dict | None = None,
    ) -> dict:
        bucket = f"CATEGORY#{category}" if category else "CATALOG#ALL"
        return self.adapter.query_page(
            "GSI1PK",
            bucket,
            index_name=self.CATALOG_INDEX,
            limit=limit,
            exclusive_start_key=cursor,
        )

    def list_categories(self) -> list[dict]:
        return self.adapter.query_items(
            "PK",
            "CATEGORIES",
            "SK",
            "CATEGORY#",
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
