"""
seed.py — Pobla la tabla DynamoDB con usuarios, órdenes y productos.

Cambios respecto al seed original:
  - Precios en COP (pesos colombianos)
  - Nuevos ítems PRODUCT#<id> / #METADATA  →  los consume /products
  - Imágenes reales (Unsplash) para cada producto
  - Más órdenes con sus ítems enlazados a los productos del catálogo
  - Usuario jgarcia (el que usa el frontend por defecto)
"""

import os
import sys
from decimal import Decimal
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings


# ─────────────────────────────────────────────
# Conexión
# ─────────────────────────────────────────────

def _dynamodb_resource():
    settings = get_settings()
    kwargs = {"region_name": settings.aws_region}

    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
    if settings.aws_secret_access_key:
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

    endpoint_override = os.environ.get("AWS_ENDPOINT_URL") or os.environ.get("AWS_ENDPOINT")
    if endpoint_override:
        kwargs["endpoint_url"] = endpoint_override
    elif settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    return boto3.resource("dynamodb", **kwargs), settings.ecommerce_table_name


# ─────────────────────────────────────────────
# Crear tabla si no existe
# ─────────────────────────────────────────────

def ensure_table_exists(dynamodb, table_name: str):
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"  ✓ Tabla '{table_name}' ya existe.")
        return table
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "ResourceNotFoundException":
            raise

    print(f"  → Creando tabla '{table_name}'...")
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print(f"  ✓ Tabla creada.")
    return table


# ─────────────────────────────────────────────
# Datos
# ─────────────────────────────────────────────

def build_items() -> list[dict]:
    items = []

    # ── USUARIOS ────────────────────────────────────────────────────────────

    items += [
        # Usuario 1 — Luisa (datos originales)
        {
            "PK": "USER#1",
            "SK": "PROFILE",
            "user_id": "luisa",
            "name": "Luisa García",
            "email": "luisa@mercado.com",
            "addresses": ["Calle 10, Bogotá", "Ave. 5, Medellín"],
            "payments": ["Visa ...1234", "PayPal"],
            "avatar_url": "https://i.pravatar.cc/150?u=luisa",
            "default_address": "Calle 10, Bogotá",
        },
        # Usuario 2 — Carlos (datos originales)
        {
            "PK": "USER#2",
            "SK": "PROFILE",
            "user_id": "carlos",
            "name": "Carlos Martínez",
            "email": "carlos@mercado.com",
            "addresses": ["Cra 45, Cali"],
            "payments": ["Mastercard ...8899"],
            "avatar_url": "https://i.pravatar.cc/150?u=carlos",
            "default_address": "Cra 45, Cali",
        },
        # Usuario 3 — jgarcia (el que usa el frontend por defecto)
        {
            "PK": "USER#jgarcia",
            "SK": "PROFILE",
            "user_id": "jgarcia",
            "name": "Juan García",
            "email": "jgarcia@x.com",
            "addresses": ["Calle 100 # 12-34, Apto 501, Bogotá", "Av. El Dorado 68-50, Bogotá"],
            "payments": ["Visa ...4321", "PayPal"],
            "avatar_url": "https://i.pravatar.cc/150?u=jgarcia",
            "default_address": "Calle 100 # 12-34, Apto 501, Bogotá, Colombia",
        },
    ]

    # ── ÓRDENES DE USUARIO 1 (Luisa) ────────────────────────────────────────

    items += [
        {
            "PK": "USER#1",
            "SK": "ORDER#202311151430",
            "id": "ORD#553",
            "status": "Pago exitoso",
            "created_at": "2023-11-15T14:30Z",
            "shipping_address": "Calle 10",
            "total": Decimal("540000"),
        },
        {
            "PK": "USER#1",
            "SK": "ORDER#202311010915",
            "id": "ORD#554",
            "status": "Enviado",
            "created_at": "2023-11-01T09:15Z",
            "shipping_address": "Calle 10",
            "total": Decimal("830000"),
        },
        {
            "PK": "USER#1",
            "SK": "ORDER#202310270800",
            "id": "ORD#555",
            "status": "Pago exitoso",
            "created_at": "2023-10-27T08:00Z",
            "shipping_address": "Calle 10",
            "total": Decimal("1250000"),
        },
        {
            "PK": "USER#1",
            "SK": "ORDER#202312021000",
            "id": "ORD#556",
            "status": "En preparacion",
            "created_at": "2023-12-02T10:00Z",
            "shipping_address": "Ave. 5, Medellín",
            "total": Decimal("320000"),
        },
    ]

    # ── DETALLES E ÍTEMS DE ÓRDENES (Luisa) ─────────────────────────────────

    items += [
        # ORD#553
        {
            "PK": "ORDER#553",
            "SK": "DETAILS",
            "order_id": "ORD#553",
            "date": "2023-11-15T14:30Z",
            "status": "Pago exitoso",
            "shipping_address": "Calle 10, Bogotá",
            "total": Decimal("540000"),
        },
        {
            "PK": "ORDER#553",
            "SK": "ITEM#1",
            "product_id": "p3",
            "name": "Auriculares Bluetooth Z5",
            "quantity": 2,
            "unit_price": Decimal("120000"),
            "subtotal": Decimal("240000"),
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=60&h=60&fit=crop",
        },
        {
            "PK": "ORDER#553",
            "SK": "ITEM#2",
            "product_id": "p6",
            "name": "Camiseta Algodón Hombre",
            "quantity": 2,
            "unit_price": Decimal("45000"),
            "subtotal": Decimal("90000"),
            "image_url": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=60&h=60&fit=crop",
        },

        # ORD#555
        {
            "PK": "ORDER#555",
            "SK": "DETAILS",
            "order_id": "ORD#555",
            "date": "2023-10-27T08:00Z",
            "status": "Pago exitoso",
            "shipping_address": "Calle 10, Bogotá",
            "total": Decimal("1250000"),
        },
        {
            "PK": "ORDER#555",
            "SK": "ITEM#1",
            "product_id": "p2",
            "name": "Portátil WorkPro 15",
            "quantity": 1,
            "unit_price": Decimal("2200000"),
            "subtotal": Decimal("2200000"),
            "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=60&h=60&fit=crop",
        },
        {
            "PK": "ORDER#555",
            "SK": "ITEM#2",
            "product_id": "p6",
            "name": "Camiseta Algodón Hombre",
            "quantity": 2,
            "unit_price": Decimal("45000"),
            "subtotal": Decimal("90000"),
            "image_url": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=60&h=60&fit=crop",
        },

        # ORD#556
        {
            "PK": "ORDER#556",
            "SK": "DETAILS",
            "order_id": "ORD#556",
            "date": "2023-12-02T10:00Z",
            "status": "En preparacion",
            "shipping_address": "Ave. 5, Medellín",
            "total": Decimal("320000"),
        },
        {
            "PK": "ORDER#556",
            "SK": "ITEM#1",
            "product_id": "p8",
            "name": "Teclado Mecánico RGB",
            "quantity": 1,
            "unit_price": Decimal("280000"),
            "subtotal": Decimal("280000"),
            "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=60&h=60&fit=crop",
        },
    ]

    # ── ÓRDENES DE USUARIO 2 (Carlos) ───────────────────────────────────────

    items += [
        {
            "PK": "USER#2",
            "SK": "ORDER#202312051830",
            "id": "ORD#900",
            "status": "Pago exitoso",
            "created_at": "2023-12-05T18:30Z",
            "shipping_address": "Cra 45, Cali",
            "total": Decimal("470000"),
        },
        {
            "PK": "ORDER#900",
            "SK": "DETAILS",
            "order_id": "ORD#900",
            "date": "2023-12-05T18:30Z",
            "status": "Pago exitoso",
            "shipping_address": "Cra 45, Cali",
            "total": Decimal("470000"),
        },
        {
            "PK": "ORDER#900",
            "SK": "ITEM#1",
            "product_id": "p8",
            "name": "Teclado Mecánico RGB",
            "quantity": 1,
            "unit_price": Decimal("280000"),
            "subtotal": Decimal("280000"),
            "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=60&h=60&fit=crop",
        },
    ]

    # ── ÓRDENES DE jgarcia ───────────────────────────────────────────────────

    items += [
        {
            "PK": "USER#jgarcia",
            "SK": "ORDER#202311151436",
            "id": "ORD#200",
            "status": "Pago exitoso",
            "created_at": "2023-11-15T14:36Z",
            "shipping_address": "Calle 100 # 12-34, Apto 501",
            "total": Decimal("970000"),
        },
        {
            "PK": "USER#jgarcia",
            "SK": "ORDER#202311010915",
            "id": "ORD#201",
            "status": "Enviado",
            "created_at": "2023-11-01T09:15Z",
            "shipping_address": "Calle 100 # 12-34, Apto 501",
            "total": Decimal("350000"),
        },
        {
            "PK": "USER#jgarcia",
            "SK": "ORDER#202310270800",
            "id": "ORD#202",
            "status": "Pago exitoso",
            "created_at": "2023-10-27T08:00Z",
            "shipping_address": "Av. El Dorado 68-50",
            "total": Decimal("2200000"),
        },
        {
            "PK": "USER#jgarcia",
            "SK": "ORDER#202310101145",
            "id": "ORD#203",
            "status": "Enviado",
            "created_at": "2023-10-10T11:45Z",
            "shipping_address": "Av. El Dorado 68-50",
            "total": Decimal("120000"),
        },
        {
            "PK": "USER#jgarcia",
            "SK": "ORDER#202309251600",
            "id": "ORD#204",
            "status": "Pago exitoso",
            "created_at": "2023-09-25T16:00Z",
            "shipping_address": "Calle 100 # 12-34, Apto 501",
            "total": Decimal("850000"),
        },

        # Detalles e ítems de jgarcia
        {
            "PK": "ORDER#200",
            "SK": "DETAILS",
            "order_id": "ORD#200",
            "date": "2023-11-15T14:36Z",
            "status": "Pago exitoso",
            "shipping_address": "Calle 100 # 12-34, Apto 501, Bogotá",
            "total": Decimal("970000"),
        },
        {
            "PK": "ORDER#200",
            "SK": "ITEM#1",
            "product_id": "p4",
            "name": "Reloj Inteligente FitTrack",
            "quantity": 1,
            "unit_price": Decimal("350000"),
            "subtotal": Decimal("350000"),
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=60&h=60&fit=crop",
        },
        {
            "PK": "ORDER#200",
            "SK": "ITEM#2",
            "product_id": "p8",
            "name": "Teclado Mecánico RGB",
            "quantity": 1,
            "unit_price": Decimal("280000"),
            "subtotal": Decimal("280000"),
            "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=60&h=60&fit=crop",
        },
        {
            "PK": "ORDER#201",
            "SK": "DETAILS",
            "order_id": "ORD#201",
            "date": "2023-11-01T09:15Z",
            "status": "Enviado",
            "shipping_address": "Calle 100 # 12-34, Apto 501, Bogotá",
            "total": Decimal("350000"),
        },
        {
            "PK": "ORDER#201",
            "SK": "ITEM#1",
            "product_id": "p4",
            "name": "Reloj Inteligente FitTrack",
            "quantity": 1,
            "unit_price": Decimal("350000"),
            "subtotal": Decimal("350000"),
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=60&h=60&fit=crop",
        },
        {
            "PK": "ORDER#202",
            "SK": "DETAILS",
            "order_id": "ORD#202",
            "date": "2023-10-27T08:00Z",
            "status": "Pago exitoso",
            "shipping_address": "Av. El Dorado 68-50, Bogotá",
            "total": Decimal("2200000"),
        },
        {
            "PK": "ORDER#202",
            "SK": "ITEM#1",
            "product_id": "p2",
            "name": "Portátil WorkPro 15",
            "quantity": 1,
            "unit_price": Decimal("2200000"),
            "subtotal": Decimal("2200000"),
            "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=60&h=60&fit=crop",
        },
        {
            "PK": "ORDER#203",
            "SK": "DETAILS",
            "order_id": "ORD#203",
            "date": "2023-10-10T11:45Z",
            "status": "Enviado",
            "shipping_address": "Av. El Dorado 68-50, Bogotá",
            "total": Decimal("120000"),
        },
        {
            "PK": "ORDER#203",
            "SK": "ITEM#1",
            "product_id": "p3",
            "name": "Auriculares Bluetooth Z5",
            "quantity": 1,
            "unit_price": Decimal("120000"),
            "subtotal": Decimal("120000"),
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=60&h=60&fit=crop",
        },
        {
            "PK": "ORDER#204",
            "SK": "DETAILS",
            "order_id": "ORD#204",
            "date": "2023-09-25T16:00Z",
            "status": "Pago exitoso",
            "shipping_address": "Calle 100 # 12-34, Apto 501, Bogotá",
            "total": Decimal("850000"),
        },
        {
            "PK": "ORDER#204",
            "SK": "ITEM#1",
            "product_id": "p1",
            "name": "Teléfono Inteligente X100",
            "quantity": 1,
            "unit_price": Decimal("850000"),
            "subtotal": Decimal("850000"),
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=60&h=60&fit=crop",
        },
    ]

    # ── PRODUCTOS ────────────────────────────────────────────────────────────
    # Patrón: PK=PRODUCT#<id>  SK=#METADATA
    # Consumido por: GET /products → lambda list_products

    items += [
        {
            "PK": "PRODUCT#p1",
            "SK": "#METADATA",
            "product_id": "p1",
            "name": "Teléfono Inteligente X100",
            "description": "Smartphone de última generación con cámara de 108 MP y batería de 5000 mAh.",
            "price": Decimal("850000"),
            "stock": 15,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p2",
            "SK": "#METADATA",
            "product_id": "p2",
            "name": "Portátil WorkPro 15",
            "description": "Laptop profesional Intel i7, 16 GB RAM, SSD 512 GB, pantalla FHD.",
            "price": Decimal("2200000"),
            "stock": 8,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p3",
            "SK": "#METADATA",
            "product_id": "p3",
            "name": "Auriculares Bluetooth Z5",
            "description": "Sonido premium inalámbrico con cancelación de ruido activa y 30 h de batería.",
            "price": Decimal("120000"),
            "stock": 25,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p4",
            "SK": "#METADATA",
            "product_id": "p4",
            "name": "Reloj Inteligente FitTrack",
            "description": "Smartwatch deportivo con GPS, monitor cardíaco y resistencia al agua IP68.",
            "price": Decimal("350000"),
            "stock": 3,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p5",
            "SK": "#METADATA",
            "product_id": "p5",
            "name": "Mochila de Viaje",
            "description": "Mochila resistente 30L con compartimento acolchado para portátil hasta 15.6\".",
            "price": Decimal("90000"),
            "stock": 50,
            "category": "Deportes",
            "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p6",
            "SK": "#METADATA",
            "product_id": "p6",
            "name": "Camiseta Algodón Hombre",
            "description": "100% algodón orgánico certificado, disponible en tallas S–XXL.",
            "price": Decimal("45000"),
            "stock": 100,
            "category": "Ropa",
            "image_url": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p7",
            "SK": "#METADATA",
            "product_id": "p7",
            "name": "Lámpara de Escritorio LED",
            "description": "Luz ajustable 3 temperaturas, carga USB integrada, brazo articulado.",
            "price": Decimal("65000"),
            "stock": 20,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p8",
            "SK": "#METADATA",
            "product_id": "p8",
            "name": "Teclado Mecánico RGB",
            "description": "Switches blue, retroiluminación RGB por tecla, layout TKL compacto.",
            "price": Decimal("280000"),
            "stock": 12,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=300&h=300&fit=crop",
        },
    ]

    return items


# ─────────────────────────────────────────────
# Inserción
# ─────────────────────────────────────────────

def seed_items(table, items: list[dict]):
    print(f"  → Insertando {len(items)} ítems...")
    with table.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as batch:
        for item in items:
            batch.put_item(Item=item)
    print(f"  ✓ Inserción completada.")


# ─────────────────────────────────────────────
# Resumen de lo que se insertó
# ─────────────────────────────────────────────

def print_summary(items: list[dict]):
    from collections import Counter
    types = Counter()
    for item in items:
        pk: str = item["PK"]
        if pk.startswith("USER#"):
            if item["SK"] == "PROFILE":
                types["Usuarios (PROFILE)"] += 1
            else:
                types["Órdenes de usuario (USER#x / ORDER#...)"] += 1
        elif pk.startswith("ORDER#"):
            if item["SK"] == "DETAILS":
                types["Detalles de orden (ORDER#x / DETAILS)"] += 1
            else:
                types["Ítems de orden (ORDER#x / ITEM#x)"] += 1
        elif pk.startswith("PRODUCT#"):
            types["Productos (PRODUCT#x / #METADATA)"] += 1

    print("\n  Resumen de ítems insertados:")
    for k, v in sorted(types.items()):
        print(f"    {v:>3}  {k}")


# ─────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🌱 Iniciando seed...\n")
    dynamodb, table_name = _dynamodb_resource()
    table = ensure_table_exists(dynamodb, table_name)
    items = build_items()
    seed_items(table, items)
    print_summary(items)
    print(f"\n✅ Seed completado en tabla: {table_name}\n")