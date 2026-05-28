from __future__ import annotations

from app.services.dynamodb_adapter import DynamoDBAdapter


class CartRepository:
    def __init__(self, adapter: DynamoDBAdapter | None = None):
        self.adapter = adapter or DynamoDBAdapter()

    def list_items(self, user_id: str) -> list[dict]:
        return self.adapter.query_items("PK", f"CART#{user_id}", "SK", "ITEM#")

    def get_item(self, user_id: str, product_id: str) -> dict | None:
        return self.adapter.get_item({"PK": f"CART#{user_id}", "SK": f"ITEM#{product_id}"})

    def put_item(self, user_id: str, item: dict) -> dict:
        record = {
            **item,
            "PK": f"CART#{user_id}",
            "SK": f"ITEM#{item['product_id']}",
            "entity_type": "CART_ITEM",
            "user_id": user_id,
        }
        return self.adapter.put_item(record) or record

    def delete_item(self, user_id: str, product_id: str) -> None:
        self.adapter.table.delete_item(
            Key={"PK": f"CART#{user_id}", "SK": f"ITEM#{product_id}"}
        )

    def clear(self, user_id: str) -> None:
        items = self.list_items(user_id)
        if not items:
            return

        with self.adapter.table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
