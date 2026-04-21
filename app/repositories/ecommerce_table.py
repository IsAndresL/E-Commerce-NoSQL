from app.services.dynamodb_adapter import DynamoDBAdapter


class ECommerceTable:
    def __init__(self, adapter: DynamoDBAdapter | None = None):
        self.adapter = adapter or DynamoDBAdapter()

    def get_user_profile(self, user_id: str):
        key = {"PK": f"USER#{user_id}", "SK": "PROFILE"}
        return self.adapter.get_item(key)

    def get_recent_orders(self, user_id: str):
        return self.adapter.query_items("PK", f"USER#{user_id}", "SK", "ORDER#")

    def get_order_details(self, order_id: str):
        key = {"PK": f"ORDER#{order_id}", "SK": "DETAILS"}
        return self.adapter.get_item(key)

    def get_order_items(self, order_id: str):
        return self.adapter.query_items("PK", f"ORDER#{order_id}", "SK", "ITEM#")

    def user_has_order(self, user_id: str, order_id: str):
        target = self._normalize_order_id(order_id)
        orders = self.get_recent_orders(user_id)
        for order in orders:
            candidate = order.get("id") or order.get("order_id") or order.get("PK")
            if self._normalize_order_id(candidate) == target:
                return True
        return False

    def _normalize_order_id(self, value):
        text = str(value or "").strip().upper()
        if text.startswith("ORDER#"):
            text = text[len("ORDER#") :]
        if text.startswith("ORD#"):
            text = text[len("ORD#") :]
        return text