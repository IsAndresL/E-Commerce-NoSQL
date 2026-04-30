from __future__ import annotations

import aioredis
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
		self._redis = None
		self.host = settings.redis_host
		self.port = settings.redis_port

	async def connect(self):
		if not self._redis:
			self._redis = await aioredis.create_redis_pool((self.host, self.port), encoding="utf-8")

	def build_key(self, kind: str, *parts: Any) -> str:
		suffix = ":".join(str(part) for part in parts if part not in (None, ""))
		base_key = f"{self.namespace}:{kind}"
		return f"{base_key}:{suffix}" if suffix else base_key

	async def get(self, key):
		await self.connect()
		value = await self._redis.get(key)
		if value:
			return json.loads(value)
		return None

	async def set(self, key, value, ex=120):
		await self.connect()
		await self._redis.set(key, json.dumps(value, default=str), expire=ex)

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


# Singleton para obtener la instancia
_cache = None


def get_redis_cache():
	global _cache
	if _cache is None:
		settings = get_settings()
		_cache = RedisCache(
			client=Redis(
				host=settings.redis_host,
				port=settings.redis_port,
				db=settings.redis_db,
				decode_responses=True,
			)
		)
	return _cache
