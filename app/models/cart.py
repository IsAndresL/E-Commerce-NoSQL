from __future__ import annotations

from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1)


class CartQuantityRequest(BaseModel):
    quantity: int = Field(default=1, ge=0)


class CartItem(BaseModel):
    product_id: str
    name: str = "Producto"
    category: str = ""
    image_url: str = ""
    unit_price: str | int | float = "0"
    quantity: int = 1
    subtotal: str | int | float = "0"
    stock_available: int = 0
    price_changed: bool = False


class CartResponse(BaseModel):
    user_id: str
    items: list[CartItem] = Field(default_factory=list)
    subtotal: str | int | float = "0"
    shipping_estimate: str | int | float = "0"
    total_estimate: str | int | float = "0"
    updated_at: str = ""
