from __future__ import annotations

import base64
import json

from pydantic import ValidationError

from app.models.ecommerce import CheckoutRequest
from app.services.ecommerce_service import ECommerceService
from lambdas.handler import created, error


def _parse_body(event: dict) -> dict:
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


def lambda_handler(event, context):
    user_id = None
    if event.get("pathParameters"):
        user_id = event["pathParameters"].get("user_id")
    user_id = user_id or event.get("user_id")

    if not user_id:
        return error("Missing user_id", status=400)

    try:
        payload = CheckoutRequest.parse_obj(_parse_body(event))
    except ValidationError as exc:
        return error(f"Invalid checkout payload: {exc}", status=400)

    service = ECommerceService()
    try:
        checkout = service.create_order(user_id, payload)
    except ValueError as exc:
        return error(str(exc), status=400)

    return created(checkout)