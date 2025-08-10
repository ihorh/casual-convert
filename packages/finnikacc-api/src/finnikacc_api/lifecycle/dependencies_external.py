"""Simple dependency injection into FastAPI `context`."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Annotated, Final

import aiohttp
import redis.asyncio as redis
from arq import ArqRedis, create_pool
from arq.connections import RedisSettings
from fastapi import Depends, FastAPI, Request
from fastapi.concurrency import asynccontextmanager

from finnikacc_api import settings


@dataclass(slots=True, kw_only=True, frozen=True)
class ExternalDependencies:
    redis: redis.Redis
    arq_redis: ArqRedis
    oex_client: aiohttp.ClientSession


EXTERNAL_DEPENDENCIES_CONTEXT_KEY: Final = "fccapi_external_dependencies"


def get_ext_deps(request: Request) -> ExternalDependencies:
    return get_ext_deps_from_app(request.app)


def get_ext_deps_from_app(app: FastAPI) -> ExternalDependencies:
    external_dependencies = app.state.fccapi_external_dependencies
    if not external_dependencies or not isinstance(external_dependencies, ExternalDependencies):
        msg = "Application's dependency injection misconfigured"
        raise RuntimeError(msg)
    return external_dependencies


def get_ext_deps_from_dict(ctx: dict) -> ExternalDependencies:
    external_dependencies = ctx.get(EXTERNAL_DEPENDENCIES_CONTEXT_KEY)
    if not external_dependencies or not isinstance(external_dependencies, ExternalDependencies):
        msg = "Application's dependency injection misconfigured"
        raise RuntimeError(msg)
    return external_dependencies


def get_redis_client(ext_deps: Annotated[ExternalDependencies, Depends(get_ext_deps)]) -> redis.Redis:
    return ext_deps.redis


RedisClientDep = Annotated[redis.Redis, Depends(get_redis_client)]


@asynccontextmanager
async def external_deps_lifespan(app: FastAPI) -> AsyncGenerator[ExternalDependencies]:
    deps = ExternalDependencies(
        redis=redis.Redis(
            host=settings.app.REDIS_HOST,
            port=settings.app.REDIS_PORT,
            db=settings.app.REDIS_DB,
        ),
        arq_redis=await create_pool(
            RedisSettings(
                host=settings.app.REDIS_HOST,
                port=settings.app.REDIS_PORT,
                database=int(settings.app.REDIS_DB),
            ),
        ),
        oex_client=aiohttp.ClientSession(
            settings.app.OEX_RATES_BASE_URL,
            headers={
                "Authorization": f"Token {settings.secret.OEX_RATES_APP_ID}",
            },
        ),
    )
    app.state.fccapi_external_dependencies = deps

    yield deps

    app.state.fccapi_external_dependencies = None

    await deps.oex_client.close()

    await deps.arq_redis.close()
    await deps.arq_redis.connection_pool.disconnect()

    await deps.redis.close()
    await deps.redis.connection_pool.disconnect()
