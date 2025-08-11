"""Simple dependency injection into FastAPI `context`."""

from collections.abc import AsyncGenerator

import aiohttp
import redis.asyncio as redis
from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from arq import ArqRedis, create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from finnikacc_api import settings
from finnikacc_api.lifecycle.dependencies import EXTERNAL_DEPENDENCIES_CONTEXT_KEY, ExternalDependencies


@asynccontextmanager
async def external_deps_lifespan(app: FastAPI) -> AsyncGenerator[ExternalDependencies]:
    deps = ExternalDependencies(
        redis=_redis_async_factory(),
        arq_redis=await _arq_redis_async_factory(),
        oex_client=_aiohttp_oex_client_factory(),
    )
    setattr(app.state, EXTERNAL_DEPENDENCIES_CONTEXT_KEY, deps)

    yield deps

    delattr(app.state, EXTERNAL_DEPENDENCIES_CONTEXT_KEY)

    await deps.oex_client.close()

    await deps.arq_redis.close()
    await deps.arq_redis.connection_pool.disconnect()

    await deps.redis.close()
    await deps.redis.connection_pool.disconnect()


def _redis_async_factory() -> redis.Redis:
    if settings.app.REDIS_CONNECTION_STRING:
        return redis.Redis.from_url(settings.app.REDIS_CONNECTION_STRING)
    if settings.app.REDIS_HOST and settings.app.REDIS_PORT:
        return redis.Redis(
            host=settings.app.REDIS_HOST,
            port=settings.app.REDIS_PORT,
            db=settings.app.REDIS_DB or 0,
        )
    msg = "Redis connection details misconfigured"
    raise RuntimeError(msg)


async def _arq_redis_async_factory() -> ArqRedis:
    redis_settings = None
    if settings.app.REDIS_CONNECTION_STRING:
        redis_settings = RedisSettings.from_dsn(settings.app.REDIS_CONNECTION_STRING)
    elif settings.app.REDIS_HOST and settings.app.REDIS_PORT:
        redis_settings = RedisSettings(
            host=settings.app.REDIS_HOST,
            port=settings.app.REDIS_PORT,
            database=int(settings.app.REDIS_DB) if settings.app.REDIS_DB else 0,
        )
    else:
        msg = "Redis connection details misconfigured"
        raise RuntimeError(msg)

    return await create_pool(redis_settings)


def _aiohttp_oex_client_factory() -> aiohttp.ClientSession:
    return CachedSession(
        settings.app.OEX_RATES_BASE_URL,
        headers={
            "Authorization": f"Token {settings.secret.OEX_RATES_APP_ID}",
        },
        allow_redirects=False,
        # ! Due to limit on number of requests per month, this fool-proof
        # * cache is required in order not to use all limit
        # * because of stupid bug or anything like that
        # in prod env can be disabled (set expiration to 0)
        # or configured to expire in few minutes.
        cache=SQLiteBackend(
            settings.app.OEX_CACHE_DB_NAME,
            expire_after=settings.app.OEX_CACHE_EXPIRE_AFTER_SEC,
        ),
    )
