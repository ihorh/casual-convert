import logging
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from finnikacc_api.app_webapi.main import app_webapi
from finnikacc_api.lifecycle.arq_lifecycle import arq_lifespan
from finnikacc_api.lifecycle.deps_ext_lifecycle import external_deps_lifespan
from finnikacc_api.lifecycle.deps_int_lifecycle import internal_deps_lifespan

LOG = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with AsyncExitStack() as stack:
        _deps = await stack.enter_async_context(external_deps_lifespan(app))
        _ideps = await stack.enter_async_context(internal_deps_lifespan(app))
        _wrk = await stack.enter_async_context(arq_lifespan(app))
        LOG.info("App lifespan initialization completed.")
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/status")
async def get_status() -> dict[str, str]:
    return {"status": "Happy Finnika! :-)"}


app_api = FastAPI()

app.mount("/api-web-app", app_webapi)
app.mount("/api", app_api)
