from app.services.dynamodb_adapter import DynamoDBAdapter


class ProductRepository:
    def __init__(self, adapter: DynamoDBAdapter | None = None):
        self.adapter = adapter or DynamoDBAdapter()

    def list_products(self) -> list[dict]:
        return self.adapter.query_items("PK", "PRODUCTS", "SK", "PRODUCT#")

    def get_product(self, product_id: str) -> dict | None:
        return self.adapter.get_item({"PK": "PRODUCTS", "SK": f"PRODUCT#{product_id}"})