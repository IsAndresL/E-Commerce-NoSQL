from __future__ import annotations

from typing import Any, Mapping

from app.repositories.product_repo import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository | None = None):
        self.repo = repo or ProductRepository()

    def list_products(self) -> list[dict]:
        items = self.repo.list_products() or []
        return [self._normalize_product(item) for item in items]

    def get_product(self, product_id: str) -> dict | None:
        item = self.repo.get_product(product_id)
        if not item:
            return None
        return self._normalize_product(item)

    def _normalize_product(self, item: Mapping[str, Any]) -> dict:
        return {
            "id":          self._pick_str(item, "SK", default="").replace("PRODUCT#", ""),
            "name":        self._pick_str(item, "name", default="Sin nombre"),
            "price":       self._pick_number(item, "price", default=0),
            "stock":       self._pick_int(item, "stock", default=0),
            "category":    self._pick_str(item, "category", default="General"),
            "description": self._pick_str(item, "description", default=""),
            "image":       self._pick_str(item, "image", default=""),
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