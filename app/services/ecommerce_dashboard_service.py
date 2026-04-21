from app.repositories.ecommerce_table import ECommerceTable

class ECommerceDashboardService:
    def __init__(self, table: ECommerceTable | None = None):
        self.table = table or ECommerceTable()

    def build_dashboard(self, user_id: str, order_id: str):
        profile = self.table.get_user_profile(user_id) or {}
        orders = self.table.get_recent_orders(user_id) or []
        requested_order_id = self._normalize_order_id(order_id)
        user_has_order = any(
            self._normalize_order_id(order.get("id") or order.get("order_id") or order.get("PK")) == requested_order_id
            for order in orders
        )

        if user_has_order:
            order_details = self.table.get_order_details(order_id) or {}
            items = self.table.get_order_items(order_id) or []
        else:
            order_details = {}
            items = []

        return {
            "user_id": user_id,
            "order_id": order_id,
            "profile": self._normalize_profile(profile),
            "orders": [self._normalize_order(order) for order in orders],
            "order_details": self._normalize_order_details(order_details),
            "items": [self._normalize_item(item) for item in items],
        }

    def _normalize_profile(self, profile: dict):
        return {
            "name": self._pick(profile, "name", "Nombre", "full_name", default="Sin nombre"),
            "email": self._pick(profile, "email", "Correo", "correo", default="sin-correo@local"),
            "addresses": self._pick_list(profile, "addresses", "Direcciones", "address", default=["Sin direccion"]),
            "payments": self._pick_list(profile, "payments", "Metodos de pago", "payment_methods", default=["Sin metodos"]),
        }

    def _normalize_order(self, order: dict):
        return {
            "id": self._pick(order, "id", "order_id", "PK", default="ORD#000"),
            "status": self._pick(order, "status", "Estado", "payment_status", default="Pendiente"),
            "created_at": self._pick(order, "created_at", "Fecha", "date", default="-"),
            "shipping_address": self._pick(order, "shipping_address", "DireccionEnvio", "Direccion de envio", default="-"),
            "total": self._pick(order, "total", "Total", default="0"),
        }

    def _normalize_order_details(self, order_details: dict):
        return {
            "order_id": self._pick(order_details, "order_id", "id", "PK", default="ORD#000"),
            "date": self._pick(order_details, "date", "Fecha", default="-"),
            "status": self._pick(order_details, "status", "Estado", "payment_status", default="Pendiente"),
            "shipping_address": self._pick(order_details, "shipping_address", "DireccionEnvio", default="-"),
            "total": self._pick(order_details, "total", "Total", default="0"),
        }

    def _normalize_item(self, item: dict):
        return {
            "name": self._pick(item, "name", "Nombre", "product_name", default="Producto"),
            "quantity": self._pick(item, "quantity", "Cantidad", default="1"),
            "unit_price": self._pick(item, "unit_price", "Precio", "Precio_Unitario_Compra", default="0"),
            "subtotal": self._pick(item, "subtotal", "Subtotal", default="0"),
        }

    def _pick(self, data: dict, *keys, default=None):
        for key in keys:
            value = data.get(key)
            if value not in (None, ""):
                return value
        return default

    def _pick_list(self, data: dict, *keys, default=None):
        value = self._pick(data, *keys, default=default or [])
        if isinstance(value, list):
            return value
        if value in (None, ""):
            return default or []
        return [value]

    def _normalize_order_id(self, value):
        text = str(value or "").strip().upper()
        if text.startswith("ORDER#"):
            text = text[len("ORDER#") :]
        if text.startswith("ORD#"):
            text = text[len("ORD#") :]
        return text