import json
import logging
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack

import redis.asyncio as redis
from fastapi import BackgroundTasks, FastAPI
from fastapi.concurrency import asynccontextmanager

from finnikacc_api import settings
from finnikacc_api.app_webapi.main import app_webapi
from finnikacc_api.dependencies_external import RedisClientDep, external_deps_lifespan

logging.config.fileConfig(f"config/{settings.APP_ENV}/logging.conf", disable_existing_loggers=False)  # pyright: ignore[reportAttributeAccessIssue]

LOG = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with AsyncExitStack() as stack:
        _deps = await stack.enter_async_context(external_deps_lifespan(app))
        LOG.info("App lifespan initialization completed.")
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/status")
async def get_status(background_tasks: BackgroundTasks, redis_client: RedisClientDep) -> dict[str, str]:
    background_tasks.add_task(try_redis, redis_client)
    return {"status": "Happy Finnika! :-)"}


async def try_redis(redis_client: redis.Redis) -> None:
    print("redis client test")
    r = await redis_client.keys("*")
    await redis_client.set("test_my:1234", json.dumps({"happy": "path", "sad": 13}), ex=300)
    print(r)
    r = await redis_client.get("test_my:1234")
    print(r)
    await redis_client.pubsub().su
    pass


app_api = FastAPI()

app.mount("/api-web-app", app_webapi)
app.mount("/api", app_api)
