from __future__ import annotations

import base64
import json


def parse_body(event: dict) -> dict:
    body = event.get("body")
    if not body:
        return {}

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    if isinstance(body, dict):
        return body

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}


def get_user_id(event: dict) -> str | None:
    path_params = event.get("pathParameters") or {}
    return path_params.get("user_id") or event.get("user_id")


def get_product_id(event: dict) -> str | None:
    path_params = event.get("pathParameters") or {}
    return path_params.get("product_id") or event.get("product_id")
