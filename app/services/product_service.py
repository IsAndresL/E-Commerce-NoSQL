from __future__ import annotations

import base64
import json
import unicodedata
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

    def list_products(
        self,
        category: str | None = None,
        search: str | None = None,
        limit: int = 24,
        cursor: str | None = None,
    ) -> dict:
        normalized_category = self._clean_category(category)
        normalized_search = self._normalize_text(search or "")
        safe_limit = min(max(self._coerce_int(limit, 24), 1), 48)
        cache_key = self._cache_key(
            "products",
            "page",
            normalized_category or "all",
            normalized_search or "none",
            str(safe_limit),
            cursor or "start",
        )
        cached_products = self.cache.get_json(cache_key)
        if isinstance(cached_products, dict):
            return cached_products

        page = self._query_products_page(
            category=normalized_category,
            search=normalized_search,
            limit=safe_limit,
            cursor=self._decode_cursor(cursor),
        )
        self.cache.set_json(cache_key, page, ttl_seconds=self.cache_ttl_seconds)
        return page

    def list_categories(self) -> list[dict]:
        cache_key = self._cache_key("products", "categories")
        cached_categories = self.cache.get_json(cache_key)
        if isinstance(cached_categories, list):
            return cached_categories

        categories = [
            {
                "name": self._pick_str(item, "name", default=str(item.get("SK", "")).replace("CATEGORY#", "")),
                "slug": self._pick_str(item, "slug", default=""),
                "count": self._pick_int(item, "count", default=0),
            }
            for item in self.repo.list_categories()
        ]
        categories = [item for item in categories if item["name"]]
        self.cache.set_json(cache_key, categories, ttl_seconds=self.cache_ttl_seconds)
        return categories

    def get_product(self, product_id: str) -> dict | None:
        cache_key = self._cache_key("products", product_id)
        cached_product = self.cache.get_json(cache_key)
        if isinstance(cached_product, dict):
            return self._normalize_product(cached_product)

        item = self.repo.get_product(product_id)
        if not item:
            return None
        normalized_product = self._normalize_product(item)
        self.cache.set_json(cache_key, normalized_product, ttl_seconds=self.cache_ttl_seconds)
        return normalized_product

    def _query_products_page(
        self,
        category: str | None,
        search: str,
        limit: int,
        cursor: dict | None,
    ) -> dict:
        products: list[dict] = []
        next_cursor = cursor
        read_limit = limit if not search else limit * 4

        while len(products) < limit:
            response = self.repo.list_products_page(
                category=category,
                limit=read_limit,
                cursor=next_cursor,
            )
            next_cursor = response.get("last_evaluated_key")
            page_items = response.get("items", [])

            for item in page_items:
                product = self._normalize_product(item)
                haystack = " ".join([product["name"], product["category"], product["description"]])
                if search and search not in self._normalize_text(haystack):
                    continue
                products.append(product)
                if len(products) >= limit:
                    break

            if not next_cursor:
                break

        return {
            "items": products,
            "next_cursor": self._encode_cursor(next_cursor),
            "limit": limit,
            "category": category or "",
            "search": search,
            "count": len(products),
        }

    def _normalize_product(self, item: Mapping[str, Any]) -> dict:
        product_id = self._pick_str(item, "product_id", default="")
        if not product_id:
            product_id = self._pick_str(item, "PK", default="").replace("PRODUCT#", "")

        return {
            "product_id": product_id,
            "id": product_id,
            "name": self._pick_str(item, "name", default="Sin nombre"),
            "price": self._pick_number(item, "price", default=0),
            "stock": self._pick_int(item, "stock", default=0),
            "category": self._pick_str(item, "category", default="General"),
            "description": self._pick_str(item, "description", default=""),
            "image_url": self._pick_str(item, "image_url", "image", default=""),
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

    def _coerce_int(self, value: Any, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _clean_category(self, category: str | None) -> str | None:
        if not category:
            return None
        value = str(category).strip()
        return value if value and value.lower() not in {"todos", "all"} else None

    def _normalize_text(self, value: str) -> str:
        normalized = unicodedata.normalize("NFD", str(value).lower())
        return "".join(char for char in normalized if unicodedata.category(char) != "Mn").strip()

    def _encode_cursor(self, cursor: dict | None) -> str:
        if not cursor:
            return ""
        raw = json.dumps(cursor, default=str, separators=(",", ":"))
        return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")

    def _decode_cursor(self, cursor: str | None) -> dict | None:
        if not cursor:
            return None
        try:
            raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
            return json.loads(raw)
        except Exception:
            return None

    def _cache_key(self, kind: str, *parts: str) -> str:
        suffix = ":".join(str(part).strip() for part in parts if str(part).strip())
        return f"ecommerce:{self.CACHE_VERSION}:{kind}:{suffix}" if suffix else f"ecommerce:{self.CACHE_VERSION}:{kind}"


def list_products() -> dict:
    return ProductService().list_products()
