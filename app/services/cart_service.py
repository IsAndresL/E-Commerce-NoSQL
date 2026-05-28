from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Iterable

from app.core.config import get_settings
from app.db.redis import get_redis_cache
from app.models.cart import CartItem, CartResponse
from app.repositories.cart_repo import CartRepository
from app.repositories.product_repo import ProductRepository


class CartService:
    CACHE_VERSION = "v3"

    def __init__(
        self,
        repo: CartRepository | None = None,
        product_repo: ProductRepository | None = None,
    ):
        self.repo = repo or CartRepository()
        self.product_repo = product_repo or ProductRepository()
        self.cache = get_redis_cache()
        self.cache_ttl_seconds = max(get_settings().redis_cache_ttl_seconds, 86400)

    def get_cart(self, user_id: str) -> CartResponse:
        cache_key = self._cache_key(user_id)
        cached_cart = self.cache.get_json(cache_key)
        if isinstance(cached_cart, dict):
            return CartResponse.parse_obj(cached_cart)

        cart = self._build_cart(user_id, self.repo.list_items(user_id))
        self._cache_cart(cart)
        return cart

    def add_item(self, user_id: str, product_id: str, quantity: int = 1) -> CartResponse:
        quantity = self._coerce_quantity(quantity)
        current = self.repo.get_item(user_id, product_id)
        new_quantity = quantity + self._coerce_quantity(current.get("quantity", 0), minimum=0) if current else quantity
        self._save_item(user_id, product_id, new_quantity)
        return self._refresh_cart(user_id)

    def update_item(self, user_id: str, product_id: str, quantity: int) -> CartResponse:
        quantity = self._coerce_quantity(quantity, minimum=0)
        if quantity <= 0:
            self.repo.delete_item(user_id, product_id)
        else:
            self._save_item(user_id, product_id, quantity)
        return self._refresh_cart(user_id)

    def remove_item(self, user_id: str, product_id: str) -> CartResponse:
        self.repo.delete_item(user_id, product_id)
        return self._refresh_cart(user_id)

    def clear_cart(self, user_id: str) -> CartResponse:
        self.repo.clear(user_id)
        cart = CartResponse(user_id=user_id, updated_at=self._now())
        self._cache_cart(cart)
        return cart

    def invalidate_cache(self, user_id: str) -> None:
        self.cache.delete(self._cache_key(user_id))

    def get_checkout_items(self, user_id: str) -> list[CartItem]:
        return self.get_cart(user_id).items

    def _save_item(self, user_id: str, product_id: str, quantity: int) -> None:
        product = self.product_repo.get_product(product_id)
        if not product:
            raise ValueError(f"Producto {product_id} no existe")

        stock = self._coerce_quantity(product.get("stock", 0), minimum=0)
        if quantity > stock:
            raise ValueError(f"Stock insuficiente para {product_id}")

        now = self._now()
        existing = self.repo.get_item(user_id, product_id) or {}
        self.repo.put_item(
            user_id,
            {
                "product_id": product_id,
                "quantity": quantity,
                "price_snapshot": self._coerce_decimal(product.get("price")),
                "name_snapshot": str(product.get("name") or "Producto"),
                "image_url_snapshot": str(product.get("image_url") or ""),
                "category_snapshot": str(product.get("category") or ""),
                "updated_at": now,
                "added_at": existing.get("added_at") or now,
            },
        )

    def _refresh_cart(self, user_id: str) -> CartResponse:
        cart = self._build_cart(user_id, self.repo.list_items(user_id))
        self._cache_cart(cart)
        return cart

    def _build_cart(self, user_id: str, records: Iterable[dict[str, Any]]) -> CartResponse:
        items: list[CartItem] = []
        subtotal = Decimal("0")

        for record in records:
            product_id = str(record.get("product_id") or "").strip()
            if not product_id:
                continue

            product = self.product_repo.get_product(product_id) or {}
            quantity = self._coerce_quantity(record.get("quantity", 1))
            unit_price = self._coerce_decimal(product.get("price", record.get("price_snapshot", 0)))
            snapshot_price = self._coerce_decimal(record.get("price_snapshot", unit_price))
            item_subtotal = unit_price * Decimal(quantity)
            subtotal += item_subtotal

            items.append(
                CartItem(
                    product_id=product_id,
                    name=str(product.get("name") or record.get("name_snapshot") or "Producto"),
                    category=str(product.get("category") or record.get("category_snapshot") or ""),
                    image_url=str(product.get("image_url") or record.get("image_url_snapshot") or ""),
                    unit_price=unit_price,
                    quantity=quantity,
                    subtotal=item_subtotal,
                    stock_available=self._coerce_quantity(product.get("stock", 0), minimum=0),
                    price_changed=unit_price != snapshot_price,
                )
            )

        shipping = Decimal("0") if subtotal >= Decimal("180000") or not items else Decimal("14900")
        return CartResponse(
            user_id=user_id,
            items=items,
            subtotal=subtotal,
            shipping_estimate=shipping,
            total_estimate=subtotal + shipping,
            updated_at=self._now(),
        )

    def _cache_cart(self, cart: CartResponse) -> None:
        self.cache.set_json(self._cache_key(cart.user_id), cart.dict(), ttl_seconds=self.cache_ttl_seconds)

    def _cache_key(self, user_id: str) -> str:
        return f"ecommerce:{self.CACHE_VERSION}:cart:{user_id}"

    def _coerce_decimal(self, value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    def _coerce_quantity(self, value: Any, minimum: int = 1) -> int:
        try:
            return max(minimum, int(Decimal(str(value))))
        except Exception:
            return minimum

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
