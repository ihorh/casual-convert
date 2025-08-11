"""Simple dependency injection into FastAPI `context`."""

from collections.abc import AsyncGenerator
from datetime import timedelta

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from finnikacc_api.lifecycle.dependencies import (
    INTERNAL_DEPENDENCIES_CONTEXT_KEY,
    InternalDependencies,
    get_ext_deps_from_app,
)
from finnikacc_api.redis.redis_cache import CurrencyRateRedisCache, LastRequestETagRedisCache


@asynccontextmanager
async def internal_deps_lifespan(app: FastAPI) -> AsyncGenerator[InternalDependencies]:
    deps_ext = get_ext_deps_from_app(app)
    deps = InternalDependencies(
        currency_rate_cache=CurrencyRateRedisCache(
            deps_ext.redis,
            expiration_seconds=int(timedelta(hours=2).total_seconds()),
            cache_type="latest",
        ),
        last_request_etag_cache=LastRequestETagRedisCache(
            deps_ext.redis,
            expiration_seconds=int(timedelta(hours=2).total_seconds()),
        ),
    )
    setattr(app.state, INTERNAL_DEPENDENCIES_CONTEXT_KEY, deps)

    yield deps

    delattr(app.state, INTERNAL_DEPENDENCIES_CONTEXT_KEY)
