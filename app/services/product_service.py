from __future__ import annotations

from typing import Any, Mapping

from app.core.config import get_settings
from app.db.redis import get_redis_cache
from app.repositories.product_repo import ProductRepository


class ProductService:
    CACHE_VERSION = "v3"

    def __init__(self, repo: ProductRepository | None = None):
        self.repo = repo or ProductRepository()
        self.cache = get_redis_cache()
        self.cache_ttl_seconds = get_settings().redis_cache_ttl_seconds

    def list_products(self) -> list[dict]:
        cache_key = f"ecommerce:{self.CACHE_VERSION}:products:list"
        cached_products = self.cache.get_json(cache_key)
        if isinstance(cached_products, list):
            return [self._normalize_product(item) for item in cached_products]

        items = self.repo.list_products() or []
        normalized_products = [self._normalize_product(item) for item in items]
        if normalized_products:
            self.cache.set_json(
                cache_key,
                normalized_products,
                ttl_seconds=self.cache_ttl_seconds,
            )
        return normalized_products

    def get_product(self, product_id: str) -> dict | None:
        cache_key = f"ecommerce:{self.CACHE_VERSION}:products:{product_id}"
        cached_product = self.cache.get_json(cache_key)
        if isinstance(cached_product, dict):
            return self._normalize_product(cached_product)

        item = self.repo.get_product(product_id)
        if not item:
            return None
        normalized_product = self._normalize_product(item)
        self.cache.set_json(cache_key, normalized_product, ttl_seconds=self.cache_ttl_seconds)
        return normalized_product

    def _normalize_product(self, item: Mapping[str, Any]) -> dict:
        return {
            "product_id":  self._pick_str(item, "product_id", "SK", default="").replace("PRODUCT#", ""),
            "id":          self._pick_str(item, "product_id", "SK", default="").replace("PRODUCT#", ""),
            "name":        self._pick_str(item, "name", default="Sin nombre"),
            "price":       self._pick_number(item, "price", default=0),
            "stock":       self._pick_int(item, "stock", default=0),
            "category":    self._pick_str(item, "category", default="General"),
            "description": self._pick_str(item, "description", default=""),
            "image_url":   self._pick_str(item, "image_url", "image", default=""),
        }

    def _pick(self, data: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
        for key in keys:
            value = data.get(key)
            if value not in (None, ""):
                return value
        return default

    def _pick_str(self, data: Mapping[str, Any], *keys: str, default: str) -> str:
        value = self._pick(data, *keys, default=default)
        return str(value) if value not in (None, "") else default

    def _pick_number(self, data: Mapping[str, Any], *keys: str, default: float) -> float:
        value = self._pick(data, *keys, default=default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _pick_int(self, data: Mapping[str, Any], *keys: str, default: int) -> int:
        value = self._pick(data, *keys, default=default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default


# Función suelta para compatibilidad con código que la llama directamente
def list_products() -> list[dict]:
    return ProductService().list_products()