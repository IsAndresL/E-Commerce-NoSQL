from __future__ import annotations

from typing import Any, Mapping

from app.models.ecommerce import OrderDetails, OrderItem, OrderSummary, UserProfile
from app.repositories.ecommerce_table import ECommerceTable


class ECommerceService:
    def __init__(self, table: ECommerceTable | None = None):
        self.table = table or ECommerceTable()

    def get_user_profile(self, user_id: str) -> UserProfile | None:
        profile = self.table.get_user_profile(user_id)
        if not profile:
            return None
        return self._normalize_profile(profile)

    def get_recent_orders(self, user_id: str) -> list[OrderSummary]:
        orders = self.table.get_recent_orders(user_id) or []
        return [self._normalize_order(order) for order in orders]

    def get_order_details(self, order_id: str) -> OrderDetails | None:
        details = self.table.get_order_details(order_id)
        if not details:
            return None
        return self._normalize_order_details(details)

    def get_order_items(self, order_id: str) -> list[OrderItem]:
        items = self.table.get_order_items(order_id) or []
        return [self._normalize_item(item) for item in items]

    def user_has_order(self, user_id: str, order_id: str) -> bool:
        return self.table.user_has_order(user_id, order_id)

    def _normalize_profile(self, profile: Mapping[str, Any]) -> UserProfile:
        return UserProfile(
            name=self._pick_str(profile, "name", "Nombre", "full_name", default="Sin nombre"),
            email=self._pick_str(profile, "email", "Correo", "correo", default="sin-correo@local"),
            addresses=self._pick_list(profile, "addresses", "Direcciones", "address", default=["Sin direccion"]),
            payments=self._pick_list(profile, "payments", "Metodos de pago", "payment_methods", default=["Sin metodos"]),
        )

    def _normalize_order(self, order: Mapping[str, Any]) -> OrderSummary:
        return OrderSummary(
            id=self._pick_str(order, "id", "order_id", "PK", default="ORD#000"),
            status=self._pick_str(order, "status", "Estado", "payment_status", default="Pendiente"),
            created_at=self._pick_str(order, "created_at", "Fecha", "date", default="-"),
            shipping_address=self._pick_str(order, "shipping_address", "DireccionEnvio", "Direccion de envio", default="-"),
            total=self._pick_number_like(order, "total", "Total", default="0"),
        )

    def _normalize_order_details(self, order_details: Mapping[str, Any]) -> OrderDetails:
        return OrderDetails(
            order_id=self._pick_str(order_details, "order_id", "id", "PK", default="ORD#000"),
            date=self._pick_str(order_details, "date", "Fecha", default="-"),
            status=self._pick_str(order_details, "status", "Estado", "payment_status", default="Pendiente"),
            shipping_address=self._pick_str(order_details, "shipping_address", "DireccionEnvio", default="-"),
            total=self._pick_number_like(order_details, "total", "Total", default="0"),
        )

    def _normalize_item(self, item: Mapping[str, Any]) -> OrderItem:
        return OrderItem(
            name=self._pick_str(item, "name", "Nombre", "product_name", default="Producto"),
            quantity=self._pick_quantity(item, "quantity", "Cantidad", default="1"),
            unit_price=self._pick_number_like(item, "unit_price", "Precio", "Precio_Unitario_Compra", default="0"),
            subtotal=self._pick_number_like(item, "subtotal", "Subtotal", default="0"),
        )

    def _pick(self, data: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
        for key in keys:
            value = data.get(key)
            if value not in (None, ""):
                return value
        return default

    def _pick_str(self, data: Mapping[str, Any], *keys: str, default: str) -> str:
        value = self._pick(data, *keys, default=default)
        return str(value) if value not in (None, "") else default

    def _pick_number_like(
        self, data: Mapping[str, Any], *keys: str, default: str | int | float
    ) -> str | int | float:
        value = self._pick(data, *keys, default=default)
        if isinstance(value, (str, int, float)):
            return value
        return default

    def _pick_quantity(self, data: Mapping[str, Any], *keys: str, default: str | int) -> str | int:
        value = self._pick(data, *keys, default=default)
        if isinstance(value, (str, int)):
            return value
        return default

    def _pick_list(self, data: Mapping[str, Any], *keys: str, default: list[str] | None = None) -> list[str]:
        value = self._pick(data, *keys, default=default or [])
        if isinstance(value, list):
            return [str(item) for item in value if item not in (None, "")]
        if value in (None, ""):
            return default or []
        return [str(value)]
