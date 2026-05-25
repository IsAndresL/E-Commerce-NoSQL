from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping

from app.core.config import get_settings
from app.db.redis import get_redis_cache
from app.models.ecommerce import OrderDetails, OrderItem, OrderSummary, UserProfile
from app.repositories.ecommerce_table import ECommerceTable


class ECommerceService:
    CACHE_VERSION = "v3"

    def __init__(self, table: ECommerceTable | None = None):
        self.table = table or ECommerceTable()
        self.cache = get_redis_cache()
        self.cache_ttl_seconds = get_settings().redis_cache_ttl_seconds

    def get_user_profile(self, user_id: str) -> UserProfile | None:
        cache_key = self._cache_key("profile", user_id)
        cached_profile = self.cache.get_json(cache_key)
        if cached_profile:
            return UserProfile.parse_obj(cached_profile)

        profile = self.table.get_user_profile(user_id)
        if not profile:
            return None
        normalized = self._normalize_profile(profile)
        self.cache.set_json(cache_key, normalized.dict(), ttl_seconds=self.cache_ttl_seconds)
        return normalized

    def list_users(self) -> list[UserProfile]:
        cache_key = self._cache_key("users", "list")
        cached_users = self.cache.get_json(cache_key)
        if isinstance(cached_users, list):
            return [UserProfile.parse_obj(user) for user in cached_users]

        users = self.table.list_user_profiles() or []
        normalized_users = [self._normalize_profile(user) for user in users]
        if normalized_users:
            self.cache.set_json(
                cache_key,
                [user.dict() for user in normalized_users],
                ttl_seconds=self.cache_ttl_seconds,
            )
        return normalized_users

    def get_recent_orders(self, user_id: str) -> list[OrderSummary]:
        cache_key = self._cache_key("orders", user_id)
        cached_orders = self.cache.get_json(cache_key)
        if isinstance(cached_orders, list):
            return [OrderSummary.parse_obj(order) for order in cached_orders]

        orders = self.table.get_recent_orders(user_id) or []
        normalized_orders = [self._normalize_order(order) for order in orders]
        if normalized_orders:
            self.cache.set_json(
                cache_key,
                [order.dict() for order in normalized_orders],
                ttl_seconds=self.cache_ttl_seconds,
            )
        return normalized_orders

    def get_order_details(self, order_id: str) -> OrderDetails | None:
        cache_key = self._cache_key("order-details", order_id)
        cached_details = self.cache.get_json(cache_key)
        if cached_details:
            return OrderDetails.parse_obj(cached_details)

        details = self.table.get_order_details(order_id)
        if not details:
            return None
        normalized = self._normalize_order_details(details)
        self.cache.set_json(cache_key, normalized.dict(), ttl_seconds=self.cache_ttl_seconds)
        return normalized

    def get_order_items(self, order_id: str) -> list[OrderItem]:
        cache_key = self._cache_key("order-items", order_id)
        cached_items = self.cache.get_json(cache_key)
        if isinstance(cached_items, list):
            return [OrderItem.parse_obj(item) for item in cached_items]

        items = self.table.get_order_items(order_id) or []
        normalized_items = [self._normalize_item(item) for item in items]
        if normalized_items:
            self.cache.set_json(
                cache_key,
                [item.dict() for item in normalized_items],
                ttl_seconds=self.cache_ttl_seconds,
            )
        return normalized_items

    def user_has_order(self, user_id: str, order_id: str) -> bool:
        return self.table.user_has_order(user_id, order_id)

    def _normalize_profile(self, profile: Mapping[str, Any]) -> UserProfile:
        payment_methods = self._pick_list(profile, "payment_methods", "payments", "Metodos de pago", default=["Sin metodos"])
        raw_user_id = self._pick_str(profile, "PK", "user_id", default="0")
        return UserProfile(
            user_id=raw_user_id.replace("USER#", ""),
            name=self._pick_str(profile, "name", "Nombre", "full_name", default="Sin nombre"),
            email=self._pick_str(profile, "email", "Correo", "correo", default="sin-correo@local"),
            addresses=self._pick_list(profile, "addresses", "Direcciones", "address", default=["Sin direccion"]),
            payments=payment_methods,
            payment_methods=payment_methods,
            avatar_url=self._pick_str(profile, "avatar_url", "avatar", default=""),
            default_address=self._pick_str(profile, "default_address", "Direccion principal", default=""),
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
            product_id=self._pick_str(item, "product_id", "id", default=""),
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
        self, data: Mapping[str, Any], *keys: str, default: str | int | float | Decimal
    ) -> str | int | float | Decimal:
        value = self._pick(data, *keys, default=default)
        if isinstance(value, (str, int, float, Decimal)):
            return value
        return default

    def _pick_quantity(self, data: Mapping[str, Any], *keys: str, default: str | int | Decimal) -> str | int | Decimal:
        value = self._pick(data, *keys, default=default)
        if isinstance(value, (str, int, Decimal)):
            return value
        return default

    def _pick_list(self, data: Mapping[str, Any], *keys: str, default: list[str] | None = None) -> list[str]:
        value = self._pick(data, *keys, default=default or [])
        if isinstance(value, list):
            return [str(item) for item in value if item not in (None, "")]
        if value in (None, ""):
            return default or []
        return [str(value)]

    def _cache_key(self, kind: str, *parts: str) -> str:
        suffix = ":".join(str(part).strip() for part in parts if str(part).strip())
        base = f"ecommerce:{self.CACHE_VERSION}:{kind}"
        return f"{base}:{suffix}" if suffix else base
