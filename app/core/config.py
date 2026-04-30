from dataclasses import dataclass
from functools import lru_cache
from os import getenv

from dotenv import load_dotenv


load_dotenv()


def _first_env(*names: str, default: str | None = None) -> str | None:
	for name in names:
		value = getenv(name)
		if value:
			return value
	return default


@dataclass(frozen=True)
class Settings:
	aws_region: str = _first_env("AWS_DEFAULT_REGION", "AWS_REGION", default="us-east-1") or "us-east-1"
	aws_access_key_id: str | None = _first_env("AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY")
	aws_secret_access_key: str | None = _first_env("AWS_SECRET_ACCESS_KEY", "AWS_SECRET_KEY")
	dynamodb_endpoint_url: str | None = _first_env("DYNAMODB_ENDPOINT_URL", "DYNAMODB_ENDPOINT")
	ecommerce_table_name: str = _first_env("ECOMMERCE_TABLE_NAME", default="ecommerce") or "ecommerce"
	redis_host: str = _first_env("REDIS_HOST", default="localhost") or "localhost"
	redis_port: int = int(_first_env("REDIS_PORT", default="6379") or "6379")
	redis_db: int = int(_first_env("REDIS_DB", default="0") or "0")
	redis_cache_ttl_seconds: int = int(_first_env("REDIS_CACHE_TTL_SECONDS", default="120") or "120")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()
