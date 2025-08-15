from dataclasses import dataclass
from typing import Annotated, Final

import aiohttp
import redis.asyncio as redis
from arq import ArqRedis
from fastapi import Depends, FastAPI, Request

from finnikacc_api.redis.redis_cache import CurrencyRateRedisCache, LastRequestETagRedisCache

INTERNAL_DEPENDENCIES_CONTEXT_KEY: Final = "fccapi_internal_dependencies"
EXTERNAL_DEPENDENCIES_CONTEXT_KEY: Final = "fccapi_external_dependencies"


@dataclass(slots=True, kw_only=True, frozen=True)
class InternalDependencies:
    currency_rate_cache: CurrencyRateRedisCache
    last_request_etag_cache: LastRequestETagRedisCache


@dataclass(slots=True, kw_only=True, frozen=True)
class ExternalDependencies:
    redis: redis.Redis
    arq_redis: ArqRedis
    oex_client: aiohttp.ClientSession


def get_int_deps(request: Request) -> InternalDependencies:
    return get_int_deps_from_app(request.app)


def get_ext_deps(request: Request) -> ExternalDependencies:
    return get_ext_deps_from_app(request.app)


def get_curr_rate_redis_cache(ideps: Annotated[InternalDependencies, Depends(get_int_deps)]) -> CurrencyRateRedisCache:
    return ideps.currency_rate_cache


CurrRateCacheDep = Annotated[CurrencyRateRedisCache, Depends(get_curr_rate_redis_cache)]


def get_redis_client(ext_deps: Annotated[ExternalDependencies, Depends(get_ext_deps)]) -> redis.Redis:
    return ext_deps.redis


RedisClientDep = Annotated[redis.Redis, Depends(get_redis_client)]


def get_int_deps_from_app(app: FastAPI) -> InternalDependencies:
    return _get_attr_from_app_context(app, INTERNAL_DEPENDENCIES_CONTEXT_KEY, InternalDependencies)


def get_int_deps_from_dict(ctx: dict) -> InternalDependencies:
    return _get_attr_from_dict_context(ctx, INTERNAL_DEPENDENCIES_CONTEXT_KEY, InternalDependencies)


def get_ext_deps_from_app(app: FastAPI) -> ExternalDependencies:
    return _get_attr_from_app_context(app, EXTERNAL_DEPENDENCIES_CONTEXT_KEY, ExternalDependencies)


def get_ext_deps_from_dict(ctx: dict) -> ExternalDependencies:
    return _get_attr_from_dict_context(ctx, EXTERNAL_DEPENDENCIES_CONTEXT_KEY, ExternalDependencies)


def _get_attr_from_app_context[T](app: FastAPI, attr_name: str, expected_type: type[T]) -> T:
    attr_val = getattr(app.state, attr_name, None)
    if not attr_val or not isinstance(attr_val, expected_type):
        msg = "Application's dependency injection misconfigured"
        raise RuntimeError(msg)
    return attr_val


def _get_attr_from_dict_context[T](ctx: dict, attr_name: str, expected_type: type[T]) -> T:
    attr_val = ctx.get(attr_name)
    if not attr_val or not isinstance(attr_val, expected_type):
        msg = "Application's dependency injection misconfigured"
        raise RuntimeError(msg)
    return attr_val
