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
        {
            "PK": "PRODUCT#p9",
            "SK": "#METADATA",
            "product_id": "p9",
            "name": "Consola Retro Mini",
            "description": "Consola compacta con juegos clásicos preinstalados y salida HDMI.",
            "price": Decimal("410000"),
            "stock": 18,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1480694313141-fce5e697ee25?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p10",
            "SK": "#METADATA",
            "product_id": "p10",
            "name": "Chaqueta Impermeable",
            "description": "Chaqueta ligera resistente a lluvia y viento, ideal para uso diario.",
            "price": Decimal("135000"),
            "stock": 30,
            "category": "Ropa",
            "image_url": "https://images.unsplash.com/photo-1523398002811-999ca8dec234?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p11",
            "SK": "#METADATA",
            "product_id": "p11",
            "name": "Set de Sábanas Premium",
            "description": "Juego de sábanas suaves en microfibra con ajuste profundo.",
            "price": Decimal("98000"),
            "stock": 24,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p12",
            "SK": "#METADATA",
            "product_id": "p12",
            "name": "Balón de Fútbol Pro",
            "description": "Balón tamaño oficial con costuras reforzadas para entrenamiento y partido.",
            "price": Decimal("76000"),
            "stock": 40,
            "category": "Deportes",
            "image_url": "https://images.unsplash.com/photo-1518604666860-9ed391f76d08?w=300&h=300&fit=crop",
        },
    ]

    items += [
        {
            "PK": "PRODUCT#p13",
            "SK": "#METADATA",
            "product_id": "p13",
            "name": "Mouse Gamer GX",
            "description": "Mouse ergonómico RGB con sensor óptico de alta precisión y 7 botones programables.",
            "price": Decimal("95000"),
            "stock": 35,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p14",
            "SK": "#METADATA",
            "product_id": "p14",
            "name": "Silla Gamer Comfort",
            "description": "Silla ergonómica reclinable con soporte lumbar y reposabrazos ajustables.",
            "price": Decimal("780000"),
            "stock": 6,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p15",
            "SK": "#METADATA",
            "product_id": "p15",
            "name": "Cafetera Espresso Barista",
            "description": "Máquina espresso de 15 bares con vaporizador para cappuccino.",
            "price": Decimal("560000"),
            "stock": 10,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p16",
            "SK": "#METADATA",
            "product_id": "p16",
            "name": "Tablet Note Plus",
            "description": "Tablet de 10 pulgadas con lápiz digital y batería de larga duración.",
            "price": Decimal("980000"),
            "stock": 11,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p17",
            "SK": "#METADATA",
            "product_id": "p17",
            "name": "Bicicleta Montaña XTrail",
            "description": "Bicicleta todo terreno con suspensión delantera y frenos de disco.",
            "price": Decimal("1450000"),
            "stock": 4,
            "category": "Deportes",
            "image_url": "https://images.unsplash.com/photo-1511994298241-608e28f14fde?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p18",
            "SK": "#METADATA",
            "product_id": "p18",
            "name": "Botella Térmica Acero",
            "description": "Botella de acero inoxidable que conserva bebidas frías y calientes por 12 horas.",
            "price": Decimal("55000"),
            "stock": 70,
            "category": "Deportes",
            "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p19",
            "SK": "#METADATA",
            "product_id": "p19",
            "name": "Zapatos Running AirFlex",
            "description": "Calzado deportivo ligero con amortiguación avanzada para correr.",
            "price": Decimal("320000"),
            "stock": 22,
            "category": "Deportes",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p20",
            "SK": "#METADATA",
            "product_id": "p20",
            "name": "Monitor UltraWide 29",
            "description": "Monitor IPS UltraWide Full HD ideal para productividad y gaming.",
            "price": Decimal("1100000"),
            "stock": 7,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p21",
            "SK": "#METADATA",
            "product_id": "p21",
            "name": "Libro Python para Todos",
            "description": "Guía completa de programación en Python desde nivel básico hasta avanzado.",
            "price": Decimal("85000"),
            "stock": 60,
            "category": "Libros",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p22",
            "SK": "#METADATA",
            "product_id": "p22",
            "name": "Freidora de Aire 5L",
            "description": "Freidora sin aceite con panel digital y múltiples programas automáticos.",
            "price": Decimal("430000"),
            "stock": 14,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1585515656973-4f2f1e8c8c18?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p23",
            "SK": "#METADATA",
            "product_id": "p23",
            "name": "Gafas de Sol Urban",
            "description": "Protección UV400 con diseño moderno y montura ligera.",
            "price": Decimal("68000"),
            "stock": 45,
            "category": "Moda",
            "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p24",
            "SK": "#METADATA",
            "product_id": "p24",
            "name": "Parlante Bluetooth Boom",
            "description": "Altavoz portátil resistente al agua con sonido envolvente.",
            "price": Decimal("210000"),
            "stock": 28,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1589003077984-894e133dabab?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p25",
            "SK": "#METADATA",
            "product_id": "p25",
            "name": "Escritorio Minimalista",
            "description": "Escritorio de madera con estructura metálica y diseño moderno.",
            "price": Decimal("520000"),
            "stock": 9,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p26",
            "SK": "#METADATA",
            "product_id": "p26",
            "name": "Cámara Deportiva ActionCam",
            "description": "Grabación 4K resistente al agua con estabilización electrónica.",
            "price": Decimal("690000"),
            "stock": 13,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p27",
            "SK": "#METADATA",
            "product_id": "p27",
            "name": "Pantalón Deportivo DryFit",
            "description": "Pantalón cómodo y transpirable ideal para entrenamiento diario.",
            "price": Decimal("72000"),
            "stock": 55,
            "category": "Ropa",
            "image_url": "https://images.unsplash.com/photo-1506629905607-d9d7d1d7f84f?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p28",
            "SK": "#METADATA",
            "product_id": "p28",
            "name": "Router WiFi 6 Turbo",
            "description": "Router de alta velocidad compatible con múltiples dispositivos.",
            "price": Decimal("340000"),
            "stock": 16,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1647427060118-4911c9821b82?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p29",
            "SK": "#METADATA",
            "product_id": "p29",
            "name": "Juego de Ollas Premium",
            "description": "Set de ollas antiadherentes de aluminio con tapas de vidrio.",
            "price": Decimal("470000"),
            "stock": 18,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1584990347449-a0b8fcb58c94?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p30",
            "SK": "#METADATA",
            "product_id": "p30",
            "name": "Drone SkyVision",
            "description": "Drone con cámara HD, control remoto y autonomía de 25 minutos.",
            "price": Decimal("1250000"),
            "stock": 5,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=300&h=300&fit=crop",
        },
    ]

    items += [
        {
            "PK": "PRODUCT#p31",
            "SK": "#METADATA",
            "product_id": "p31",
            "name": "Smart TV 55 pulgadas 4K",
            "description": "Televisor UHD 4K con HDR, sistema Smart TV y control por voz.",
            "price": Decimal("1850000"),
            "stock": 9,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p32",
            "SK": "#METADATA",
            "product_id": "p32",
            "name": "Power Bank 20000mAh",
            "description": "Batería portátil de carga rápida con puertos USB-C y USB-A.",
            "price": Decimal("115000"),
            "stock": 40,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p33",
            "SK": "#METADATA",
            "product_id": "p33",
            "name": "Ventilador Torre Silent",
            "description": "Ventilador silencioso con temporizador y 3 niveles de velocidad.",
            "price": Decimal("230000"),
            "stock": 17,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p34",
            "SK": "#METADATA",
            "product_id": "p34",
            "name": "Maleta Cabina TravelGo",
            "description": "Maleta rígida con ruedas 360° y cerradura de seguridad TSA.",
            "price": Decimal("260000"),
            "stock": 19,
            "category": "Viajes",
            "image_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p35",
            "SK": "#METADATA",
            "product_id": "p35",
            "name": "Set Mancuernas Ajustables",
            "description": "Juego de pesas ajustables ideales para entrenamiento en casa.",
            "price": Decimal("390000"),
            "stock": 12,
            "category": "Deportes",
            "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p36",
            "SK": "#METADATA",
            "product_id": "p36",
            "name": "Impresora Multifuncional WiFi",
            "description": "Impresora con escáner y copiadora compatible con impresión móvil.",
            "price": Decimal("650000"),
            "stock": 10,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p37",
            "SK": "#METADATA",
            "product_id": "p37",
            "name": "Perfume Essence Noir",
            "description": "Fragancia elegante con notas amaderadas y cítricas.",
            "price": Decimal("175000"),
            "stock": 33,
            "category": "Belleza",
            "image_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p38",
            "SK": "#METADATA",
            "product_id": "p38",
            "name": "Cepillo Eléctrico Dental",
            "description": "Cepillo recargable con temporizador inteligente y múltiples modos.",
            "price": Decimal("145000"),
            "stock": 27,
            "category": "Salud",
            "image_url": "https://images.unsplash.com/photo-1559591937-abc4c2e2d5c5?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p39",
            "SK": "#METADATA",
            "product_id": "p39",
            "name": "Sofá Modular Comfort",
            "description": "Sofá moderno de 3 puestos con cojines de alta densidad.",
            "price": Decimal("2450000"),
            "stock": 4,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p40",
            "SK": "#METADATA",
            "product_id": "p40",
            "name": "Microondas Digital 20L",
            "description": "Microondas compacto con panel digital y funciones rápidas.",
            "price": Decimal("420000"),
            "stock": 15,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p41",
            "SK": "#METADATA",
            "product_id": "p41",
            "name": "Cámara Web Full HD",
            "description": "Webcam 1080p con micrófono integrado y enfoque automático.",
            "price": Decimal("135000"),
            "stock": 38,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p42",
            "SK": "#METADATA",
            "product_id": "p42",
            "name": "Sanduchera Eléctrica",
            "description": "Sanduchera antiadherente con capacidad para dos sandwiches.",
            "price": Decimal("89000"),
            "stock": 26,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1526318896980-cf78c088247c?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p43",
            "SK": "#METADATA",
            "product_id": "p43",
            "name": "Chaqueta Denim Classic",
            "description": "Chaqueta de mezclilla estilo clásico unisex.",
            "price": Decimal("165000"),
            "stock": 29,
            "category": "Ropa",
            "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p44",
            "SK": "#METADATA",
            "product_id": "p44",
            "name": "Aspiradora Robot CleanBot",
            "description": "Robot inteligente con navegación automática y carga autónoma.",
            "price": Decimal("980000"),
            "stock": 8,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p45",
            "SK": "#METADATA",
            "product_id": "p45",
            "name": "Nintendo Switch Lite",
            "description": "Consola portátil compacta ideal para gaming en movimiento.",
            "price": Decimal("980000"),
            "stock": 14,
            "category": "Videojuegos",
            "image_url": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p46",
            "SK": "#METADATA",
            "product_id": "p46",
            "name": "Monitor Gamer 144Hz",
            "description": "Pantalla Full HD de alta tasa de refresco para gaming competitivo.",
            "price": Decimal("1250000"),
            "stock": 7,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p47",
            "SK": "#METADATA",
            "product_id": "p47",
            "name": "Patineta Urbana",
            "description": "Patineta resistente con ruedas de poliuretano y diseño moderno.",
            "price": Decimal("190000"),
            "stock": 21,
            "category": "Deportes",
            "image_url": "https://images.unsplash.com/photo-1547447134-cd3f5c716030?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p48",
            "SK": "#METADATA",
            "product_id": "p48",
            "name": "Kit Herramientas 120 piezas",
            "description": "Juego completo de herramientas para reparaciones domésticas.",
            "price": Decimal("210000"),
            "stock": 16,
            "category": "Herramientas",
            "image_url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p49",
            "SK": "#METADATA",
            "product_id": "p49",
            "name": "Smartphone Eco Lite",
            "description": "Celular económico con cámara dual y batería de larga duración.",
            "price": Decimal("520000"),
            "stock": 31,
            "category": "Electrónica",
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop",
        },
        {
            "PK": "PRODUCT#p50",
            "SK": "#METADATA",
            "product_id": "p50",
            "name": "Almohada Memory Foam",
            "description": "Almohada ergonómica con espuma viscoelástica para mayor confort.",
            "price": Decimal("78000"),
            "stock": 48,
            "category": "Hogar",
            "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300&h=300&fit=crop",
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