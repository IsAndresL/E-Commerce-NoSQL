from __future__ import annotations

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    user_id: str = "0"
    name: str = "Sin nombre"
    email: str = "sin-correo@local"
    addresses: list[str] = Field(default_factory=list)
    payments: list[str] = Field(default_factory=list)
    payment_methods: list[str] = Field(default_factory=list)
    avatar_url: str = ""
    default_address: str = ""


class OrderSummary(BaseModel):
    id: str = "ORD#000"
    status: str = "Pendiente"
    created_at: str = "-"
    shipping_address: str = "-"
    total: str | int | float = "0"


class OrderDetails(BaseModel):
    order_id: str = "ORD#000"
    date: str = "-"
    status: str = "Pendiente"
    shipping_address: str = "-"
    total: str | int | float = "0"


class OrderItem(BaseModel):
    product_id: str = ""
    name: str = "Producto"
    quantity: str | int = "1"
    unit_price: str | int | float = "0"
    subtotal: str | int | float = "0"
    image_url: str = ""


class CheckoutItem(BaseModel):
    product_id: str
    name: str = "Producto"
    quantity: str | int = "1"
    unit_price: str | int | float = "0"
    price: str | int | float | None = None
    subtotal: str | int | float | None = None
    image_url: str = ""
    category: str = ""


class CheckoutRequest(BaseModel):
    items: list[CheckoutItem] = Field(default_factory=list)
    shipping_address: str = ""
    shipping_cost: str | int | float = 0


class CheckoutResponse(BaseModel):
    user_id: str
    order_summary: OrderSummary
    order_details: OrderDetails
    items: list[OrderItem] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    user_id: str
    order_id: str
    profile: UserProfile
    orders: list[OrderSummary] = Field(default_factory=list)
    order_details: OrderDetails
    items: list[OrderItem] = Field(default_factory=list)
