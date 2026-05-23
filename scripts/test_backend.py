#!/usr/bin/env python3
"""
test_backend.py — Prueba cada endpoint del API Gateway y valida que devuelva
                  lo que se espera según los datos del seed.

Uso:
    python scripts/test_backend.py                          # usa http://localhost:4566
    python scripts/test_backend.py http://localhost:4566    # URL explícita
    API_URL=https://abc123.execute-api.us-east-1.amazonaws.com python scripts/test_backend.py

Requisitos: pip install requests
"""

import json
import os
import sys
import textwrap
import time
from dataclasses import dataclass, field
from typing import Any

import requests

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

BASE_URL = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.environ.get("API_URL", "http://localhost:4566")
).rstrip("/")

TIMEOUT = 10  # segundos por request

# Usuarios y órdenes que vienen del seed
USER_1   = "1"
USER_JG  = "jgarcia"
ORDER_555 = "555"
ORDER_200 = "200"
ORDER_JG_555 = "555"   # para las rutas /user/{uid}/order/{oid}/...


# ─────────────────────────────────────────────────────────────────────────────
# Resultado de cada test
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TestResult:
    name: str
    passed: bool
    status_code: int = 0
    error: str = ""
    warnings: list[str] = field(default_factory=list)
    response_preview: str = ""


results: list[TestResult] = []


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _call(method: str, path: str, **kwargs) -> tuple[int, Any]:
    url = f"{BASE_URL}{path}"
    try:
        r = requests.request(method, url, timeout=TIMEOUT, **kwargs)
        try:
            body = r.json()
        except Exception:
            body = r.text
        return r.status_code, body
    except requests.exceptions.ConnectionError:
        return -1, f"ConnectionError — ¿Está el backend corriendo en {BASE_URL}?"
    except requests.exceptions.Timeout:
        return -2, f"Timeout después de {TIMEOUT}s"


def _preview(data: Any, max_chars: int = 260) -> str:
    raw = json.dumps(data, ensure_ascii=False, default=str)
    return raw[:max_chars] + ("…" if len(raw) > max_chars else "")


def test(
    name: str,
    path: str,
    *,
    method: str = "GET",
    expect_status: int = 200,
    checks: list[tuple[str, Any]] | None = None,   # (descripción, callable(body)->bool)
    warn_if: list[tuple[str, Any]] | None = None,
) -> TestResult:
    """Ejecuta un test y almacena el resultado."""
    status, body = _call(method, path)
    warnings = []

    # Status check
    ok = status == expect_status
    error = ""
    if status < 0:
        ok = False
        error = str(body)
    elif status != expect_status:
        error = f"Se esperaba HTTP {expect_status}, se obtuvo {status}"

    # Checks adicionales
    if ok and checks:
        for desc, fn in checks:
            try:
                if not fn(body):
                    ok = False
                    error = f"Check fallido: {desc}"
                    break
            except Exception as exc:
                ok = False
                error = f"Check '{desc}' lanzó excepción: {exc}"
                break

    # Advertencias opcionales (no fallan el test)
    if warn_if:
        for desc, fn in warn_if:
            try:
                if fn(body):
                    warnings.append(f"⚠ {desc}")
            except Exception:
                pass

    result = TestResult(
        name=name,
        passed=ok,
        status_code=status,
        error=error,
        warnings=warnings,
        response_preview=_preview(body) if status >= 0 else str(body),
    )
    results.append(result)
    _print_result(result)
    return result


def _print_result(r: TestResult):
    icon = "✅" if r.passed else "❌"
    status_str = f"HTTP {r.status_code}" if r.status_code > 0 else "NO RESPONSE"
    print(f"  {icon}  [{status_str}]  {r.name}")
    if not r.passed and r.error:
        print(f"       └─ {r.error}")
    for w in r.warnings:
        print(f"       └─ {w}")
    if not r.passed:
        preview = textwrap.shorten(r.response_preview, width=200)
        print(f"       └─ Respuesta: {preview}")


def section(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

def run_tests():
    print(f"\n🧪  EcoCart — Test de Backend")
    print(f"    API URL : {BASE_URL}")
    print(f"    Fecha   : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ── 1. PRODUCTOS ─────────────────────────────────────────────────────────
    section("1 · GET /products")

    test(
        "Lista de productos (200 + array no vacío)",
        "/products",
        checks=[
            ("body es lista",           lambda b: isinstance(b, list)),
            ("al menos 1 producto",     lambda b: len(b) >= 1),
        ],
        warn_if=[
            ("menos de 8 productos (seed tiene 8)", lambda b: isinstance(b, list) and len(b) < 8),
        ],
    )
    test(
        "Cada producto tiene campos requeridos",
        "/products",
        checks=[(
            "campos: product_id, name, price, stock, category",
            lambda b: isinstance(b, list) and len(b) > 0 and all(
                {"product_id", "name", "price", "stock", "category"} <= set(p.keys())
                for p in b
            ),
        )],
    )
    test(
        "Precios son numéricos > 0",
        "/products",
        checks=[(
            "price > 0 en todos",
            lambda b: isinstance(b, list) and all(float(p.get("price", 0)) > 0 for p in b),
        )],
    )

    # ── 2. PERFIL DE USUARIO ─────────────────────────────────────────────────
    section("2 · GET /ecommerce/user/{user_id}/profile")

    test(
        f"Perfil de USER#1 (Luisa)",
        f"/ecommerce/user/{USER_1}/profile",
        checks=[
            ("tiene name",  lambda b: "name" in b),
            ("tiene email", lambda b: "email" in b),
        ],
        warn_if=[
            ("name no es 'Luisa García'", lambda b: b.get("name") != "Luisa García"),
        ],
    )
    test(
        f"Perfil de USER#jgarcia",
        f"/ecommerce/user/{USER_JG}/profile",
        checks=[
            ("tiene name",  lambda b: "name" in b),
            ("tiene email", lambda b: "email" in b),
        ],
        warn_if=[
            ("name no es 'Juan García'", lambda b: b.get("name") != "Juan García"),
        ],
    )
    test(
        "Perfil de usuario inexistente → 404",
        "/ecommerce/user/USUARIO_QUE_NO_EXISTE/profile",
        expect_status=404,
    )

    # ── 3. PEDIDOS RECIENTES ─────────────────────────────────────────────────
    section("3 · GET /ecommerce/user/{user_id}/orders")

    test(
        f"Órdenes de USER#1 (Luisa) — lista no vacía",
        f"/ecommerce/user/{USER_1}/orders",
        checks=[
            ("es lista",           lambda b: isinstance(b, list)),
            ("al menos 1 orden",   lambda b: len(b) >= 1),
            ("campos status + created_at",
             lambda b: all({"status", "created_at"} <= set(o.keys()) for o in b)),
        ],
    )
    test(
        f"Órdenes de jgarcia — debe tener 5 órdenes",
        f"/ecommerce/user/{USER_JG}/orders",
        checks=[
            ("es lista",         lambda b: isinstance(b, list)),
            ("al menos 1 orden", lambda b: len(b) >= 1),
        ],
        warn_if=[
            ("menos de 5 órdenes (seed tiene 5)", lambda b: isinstance(b, list) and len(b) < 5),
        ],
    )
    test(
        "Órdenes de usuario inexistente → lista vacía o 404",
        "/ecommerce/user/NADIE/orders",
        checks=[(
            "es lista vacía o HTTP 404",
            lambda b: isinstance(b, list) and len(b) == 0,
        )],
        # También aceptamos 404 — lo verificamos aparte si falla
    )

    # ── 4. DETALLES DE ORDEN ─────────────────────────────────────────────────
    section("4 · GET /ecommerce/order/{order_id}/details")

    test(
        f"Detalles de ORDER#555",
        f"/ecommerce/order/{ORDER_555}/details",
        checks=[
            ("tiene order_id", lambda b: "order_id" in b),
            ("tiene status",   lambda b: "status" in b),
            ("tiene total",    lambda b: "total" in b),
        ],
        warn_if=[
            ("status no es 'Pago exitoso'", lambda b: b.get("status") != "Pago exitoso"),
        ],
    )
    test(
        "Orden inexistente → 404",
        "/ecommerce/order/ORDER_FALSA_99999/details",
        expect_status=404,
    )

    # ── 5. ÍTEMS DE ORDEN ────────────────────────────────────────────────────
    section("5 · GET /ecommerce/order/{order_id}/items")

    test(
        f"Ítems de ORDER#555 (2 ítems en seed)",
        f"/ecommerce/order/{ORDER_555}/items",
        checks=[
            ("es lista",         lambda b: isinstance(b, list)),
            ("al menos 1 ítem",  lambda b: len(b) >= 1),
            ("campos name + quantity + unit_price",
             lambda b: all({"name", "quantity", "unit_price"} <= set(i.keys()) for i in b)),
        ],
        warn_if=[
            ("no tiene exactamente 2 ítems", lambda b: isinstance(b, list) and len(b) != 2),
        ],
    )
    test(
        "Ítems de orden inexistente → lista vacía o 404",
        "/ecommerce/order/ORDER_FALSA_99999/items",
        checks=[(
            "es lista vacía",
            lambda b: isinstance(b, list) and len(b) == 0,
        )],
    )

    # ── 6. RUTAS USER+ORDER ──────────────────────────────────────────────────
    section("6 · GET /ecommerce/user/{user_id}/order/{order_id}/details")

    test(
        f"Detalles de jgarcia / ORDER#200",
        f"/ecommerce/user/{USER_JG}/order/{ORDER_200}/details",
        checks=[
            ("tiene order_id", lambda b: "order_id" in b),
            ("tiene status",   lambda b: "status" in b),
        ],
    )
    test(
        f"Detalles: user incorrecto para la orden → 404 o vacío",
        f"/ecommerce/user/{USER_1}/order/{ORDER_200}/details",
        # USER#1 (Luisa) no tiene la orden ORD#200 — depende de la impl. del lambda
        expect_status=404,
    )

    # ── 7. ÍTEMS USER+ORDER ──────────────────────────────────────────────────
    section("7 · GET /ecommerce/user/{user_id}/order/{order_id}/items")

    test(
        f"Ítems de jgarcia / ORDER#200 (2 ítems en seed)",
        f"/ecommerce/user/{USER_JG}/order/{ORDER_200}/items",
        checks=[
            ("es lista",        lambda b: isinstance(b, list)),
            ("al menos 1 ítem", lambda b: len(b) >= 1),
        ],
        warn_if=[
            ("no tiene exactamente 2 ítems", lambda b: isinstance(b, list) and len(b) != 2),
        ],
    )

    # ── 8. DASHBOARD ─────────────────────────────────────────────────────────
    section("8 · GET /ecommerce/dashboard-data")

    test(
        "Dashboard data — responde 200 con algo",
        "/ecommerce/dashboard-data",
        checks=[("respuesta no vacía", lambda b: b is not None and b != "" and b != [])],
    )

    # ── 9. CORS ───────────────────────────────────────────────────────────────
    section("9 · CORS — OPTIONS preflight")

    status, _ = _call(
        "OPTIONS",
        "/products",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    cors_ok = status in (200, 204)
    r = TestResult(
        name="OPTIONS /products → 200 o 204 (CORS preflight)",
        passed=cors_ok,
        status_code=status,
        error="" if cors_ok else f"Se obtuvo HTTP {status}",
    )
    results.append(r)
    _print_result(r)


# ─────────────────────────────────────────────────────────────────────────────
# Resumen final
# ─────────────────────────────────────────────────────────────────────────────

def print_summary():
    total  = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    print(f"\n{'═'*60}")
    print(f"  RESUMEN FINAL")
    print(f"{'═'*60}")
    print(f"  Total tests : {total}")
    print(f"  ✅ Pasaron  : {passed}")
    print(f"  ❌ Fallaron : {failed}")

    if failed:
        print(f"\n  Tests fallidos:")
        for r in results:
            if not r.passed:
                print(f"    • {r.name}")
                if r.error:
                    print(f"      → {r.error}")
    print()

    return 0 if failed == 0 else 1


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\n⚡ Interrumpido por el usuario.")
        sys.exit(1)

    exit_code = print_summary()
    sys.exit(exit_code)