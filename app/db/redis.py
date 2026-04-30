from __future__ import annotations

import json
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


class RedisCache:
	def __init__(self, client: Redis | None = None, namespace: str = "ecommerce"):
		settings = get_settings()
		self.namespace = namespace
		self.client = client or Redis(
			host=settings.redis_host,
			port=settings.redis_port,
			db=settings.redis_db,
			decode_responses=True,
		)

	def build_key(self, kind: str, *parts: Any) -> str:
		suffix = ":".join(str(part) for part in parts if part not in (None, ""))
		base_key = f"{self.namespace}:{kind}"
		return f"{base_key}:{suffix}" if suffix else base_key

	def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
		try:
			raw_value = self.client.get(key)
			if not raw_value:
				return None
			if not isinstance(raw_value, (str, bytes, bytearray)):
				return None
			return json.loads(raw_value)
		except (RedisError, json.JSONDecodeError):
			return None

	def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
		try:
			self.client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl_seconds)
		except RedisError:
			return

	def delete(self, *keys: str) -> None:
		try:
			if keys:
				self.client.delete(*keys)
		except RedisError:
			return
