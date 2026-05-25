"""Utilidades comunes para todos los lambda handlers."""
import json
from typing import Any

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
}

def ok(data: Any) -> dict:
    if hasattr(data, "model_dump_json"):
        body = data.model_dump_json()
    elif hasattr(data, "json") and hasattr(data, "dict"):
        body = data.json()
    elif isinstance(data, list):
        body = json.dumps(
            [item.model_dump() if hasattr(item, "model_dump") else item.dict() if hasattr(item, "dict") else item for item in data]
        )
    else:
        body = json.dumps(data)
    return {"statusCode": 200, "headers": HEADERS, "body": body}

def not_found(msg: str = "Not found") -> dict:
    return {"statusCode": 404, "headers": HEADERS, "body": json.dumps({"detail": msg})}

def error(msg: str = "Internal error", status: int = 500) -> dict:
    return {"statusCode": status, "headers": HEADERS, "body": json.dumps({"detail": msg})}

def path_params(event: dict) -> dict:
    return event.get("pathParameters") or {}

def query_params(event: dict) -> dict:
    return event.get("queryStringParameters") or {}