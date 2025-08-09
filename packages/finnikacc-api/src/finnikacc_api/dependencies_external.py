from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, FastAPI, Request
from fastapi.concurrency import asynccontextmanager

from finnikacc_api import settings


@dataclass(slots=True, kw_only=True, frozen=True)
class ExternalDependencies:
    redis: redis.Redis


def get_ext_deps(request: Request) -> ExternalDependencies:
    external_dependencies = request.app.state.fccapi_external_dependencies
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
    )
    app.state.fccapi_external_dependencies = deps
    yield deps
    app.state.fccapi_external_dependencies = None
    await deps.redis.close()
    await deps.redis.connection_pool.disconnect()
