from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping

from app.core.config import get_settings
from app.db.redis import get_redis_cache
from app.models.ecommerce import CheckoutRequest, CheckoutResponse, OrderDetails, OrderItem, OrderSummary, UserProfile
from app.repositories.ecommerce_table import ECommerceTable
from app.repositories.product_repo import ProductRepository


class ECommerceService:
    CACHE_VERSION = "v3"

    def __init__(self, table: ECommerceTable | None = None):
        self.table = table or ECommerceTable()
        self.product_repo = ProductRepository()
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

    def create_order(self, user_id: str, checkout_request: CheckoutRequest) -> CheckoutResponse:
        profile = self.get_user_profile(user_id)
        if not profile:
            raise ValueError("User not found")

        if not checkout_request.items:
            raise ValueError("Cart is empty")

        now = datetime.now(timezone.utc)
        order_stamp = now.strftime("%Y%m%d%H%M%S%f")
        order_id = f"ORD#{order_stamp}"
        created_at = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        shipping_address = (
            checkout_request.shipping_address
            or profile.default_address
            or (profile.addresses[0] if profile.addresses else "Sin direccion")
        ).strip()

        order_items: list[OrderItem] = []
        records: list[dict[str, Any]] = []
        stock_reservations: dict[str, int] = {}
        total = Decimal("0")

        for index, item in enumerate(checkout_request.items, start=1):
            quantity = self._coerce_int(item.quantity, default=1)
            unit_price = self._coerce_decimal(self._first_present(item.unit_price, item.price, default="0"))
            if unit_price <= 0:
                catalog_item = self.product_repo.get_product(item.product_id) or {}
                unit_price = self._coerce_decimal(catalog_item.get("price"))

            subtotal = self._coerce_decimal(item.subtotal)
            if subtotal <= 0:
                subtotal = unit_price * Decimal(quantity)

            total += subtotal

            stock_reservations[item.product_id] = stock_reservations.get(item.product_id, 0) + quantity

            order_items.append(
                OrderItem(
                    product_id=item.product_id,
                    name=item.name,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                    image_url=item.image_url,
                )
            )
            records.append(
                {
                    "PK": f"ORDER#{order_stamp}",
                    "SK": f"ITEM#{index}",
                    "product_id": item.product_id,
                    "name": item.name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "subtotal": subtotal,
                    "image_url": item.image_url,
                    "category": item.category,
                }
            )

        shipping_cost = self._coerce_decimal(checkout_request.shipping_cost)
        total += shipping_cost

        for product_id, quantity in stock_reservations.items():
            self.product_repo.reserve_stock(product_id, quantity)

        self._invalidate_product_caches(stock_reservations.keys())

        summary = OrderSummary(
            id=order_id,
            status="Pago exitoso",
            created_at=created_at,
            shipping_address=shipping_address,
            total=total,
        )
        details = OrderDetails(
            order_id=order_id,
            date=created_at,
            status="Pago exitoso",
            shipping_address=shipping_address,
            total=total,
        )

        records.insert(
            0,
            {
                "PK": f"USER#{user_id}",
                "SK": f"ORDER#{order_stamp}",
                "id": order_id,
                "status": summary.status,
                "created_at": created_at,
                "shipping_address": shipping_address,
                "total": total,
            },
        )
        records.insert(
            1,
            {
                "PK": f"ORDER#{order_stamp}",
                "SK": "DETAILS",
                "order_id": order_id,
                "date": created_at,
                "status": details.status,
                "shipping_address": shipping_address,
                "total": total,
            },
        )

        self.table.save_order_records(records)
        self._invalidate_order_caches(user_id, order_id)

        return CheckoutResponse(user_id=user_id, order_summary=summary, order_details=details, items=order_items)

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
            image_url=self._pick_str(item, "image_url", "image", default=""),
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

    def _invalidate_order_caches(self, user_id: str, order_id: str) -> None:
        self.cache.delete(
            self._cache_key("orders", user_id),
            self._cache_key("order-details", order_id),
            self._cache_key("order-items", order_id),
            self._cache_key("dashboard", user_id, order_id),
        )

    def _invalidate_product_caches(self, product_ids) -> None:
        keys = [self._cache_key("products", "list")]
        keys.extend(self._cache_key("products", product_id) for product_id in product_ids)
        self.cache.delete(*keys)

    def _coerce_decimal(self, value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    def _coerce_int(self, value: Any, default: int = 1) -> int:
        try:
            return max(1, int(Decimal(str(value))))
        except Exception:
            return default

    def _first_present(self, *values: Any, default: Any = None) -> Any:
        for value in values:
            if value not in (None, ""):
                return value
        return default
