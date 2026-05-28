"""Utilidades comunes para todos los lambda handlers."""
import json
from decimal import Decimal
from typing import Any

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE,OPTIONS",
}

def ok(data: Any) -> dict:
    if hasattr(data, "model_dump_json"):
        body = data.model_dump_json()
    elif hasattr(data, "json") and hasattr(data, "dict"):
        body = data.json()
    elif isinstance(data, list):
        serializable = []
        for item in data:
            if hasattr(item, "model_dump"):
                serializable.append(item.model_dump())
            elif hasattr(item, "dict"):
                serializable.append(item.dict())
            else:
                serializable.append(item)
        body = json.dumps(serializable, cls=_DecimalEncoder)
    else:
        body = json.dumps(data, cls=_DecimalEncoder)
    return {"statusCode": 200, "headers": HEADERS, "body": body}


class _DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            # Prefer int when value is integral, otherwise float
            try:
                if o == o.to_integral():
                    return int(o)
            except Exception:
                pass
            return float(o)
        return super().default(o)

def created(data: Any) -> dict:
    response = ok(data)
    response["statusCode"] = 201
    return response

def not_found(msg: str = "Not found") -> dict:
    return {"statusCode": 404, "headers": HEADERS, "body": json.dumps({"detail": msg})}

def error(msg: str = "Internal error", status: int = 500) -> dict:
    return {"statusCode": status, "headers": HEADERS, "body": json.dumps({"detail": msg})}

def path_params(event: dict) -> dict:
    return event.get("pathParameters") or {}

def query_params(event: dict) -> dict:
    return event.get("queryStringParameters") or {}
