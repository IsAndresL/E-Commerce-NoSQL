from __future__ import annotations

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    name: str = "Sin nombre"
    email: str = "sin-correo@local"
    addresses: list[str] = Field(default_factory=list)
    payments: list[str] = Field(default_factory=list)


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
    name: str = "Producto"
    quantity: str | int = "1"
    unit_price: str | int | float = "0"
    subtotal: str | int | float = "0"


class DashboardResponse(BaseModel):
    user_id: str
    order_id: str
    profile: UserProfile
    orders: list[OrderSummary] = Field(default_factory=list)
    order_details: OrderDetails
    items: list[OrderItem] = Field(default_factory=list)
