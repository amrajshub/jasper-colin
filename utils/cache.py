import copy
from datetime import datetime, date
import redis.asyncio as redis
import json
import hashlib

from sqlalchemy import Enum
from database.models import StatusEnum
import settings
from typing import Union

# Initialize Redis client
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


# Helper to generate a cache key based on query params
async def make_cache_key(prefix: str, **kwargs) -> str:
    kwargs = copy.deepcopy(kwargs)
    for key, value in kwargs.items():
        if isinstance(value, datetime) or isinstance(value, date):
            kwargs[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, StatusEnum):
            kwargs[key] = str(value)
    key = json.dumps(kwargs, sort_keys=True)
    return f"{prefix}:{hashlib.md5(key.encode()).hexdigest()}"


async def get_cached_response(key: str):
    return await redis_client.get(key)


async def set_cached_response(key: str, value: Union[list, dict], ttl: int = 60):
    await redis_client.set(key, json.dumps(value, default=str), ex=ttl)


async def invalidate_cache_by_prefix(prefix: str):
    keys = await redis_client.keys(f"{prefix}:*")
    if keys:
        await redis_client.delete(*keys)
