import asyncio
import logging
from collections.abc import AsyncGenerator, Sequence

from arq import Worker
from arq.connections import RedisSettings
from arq.cron import CronJob, cron
from arq.typing import StartupShutdown, WorkerCoroutine
from arq.worker import Function, create_worker
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from finnikacc_api import settings
from finnikacc_api.lifecycle.dependencies_external import (
    EXTERNAL_DEPENDENCIES_CONTEXT_KEY,
    get_ext_deps_from_app,
)

LOG = logging.getLogger(__name__)


async def _arq_worker_health_log(ctx: dict) -> None:
    LOG.debug("arq worker health check log: ")


_REDIS_SETTINGS = RedisSettings(
    host=settings.app.REDIS_HOST, port=settings.app.REDIS_PORT, database=int(settings.app.REDIS_DB),
)


class ArqWorkerSettings:
    functions: Sequence[WorkerCoroutine | Function]
    cron_jobs: Sequence[CronJob] | None = [cron(_arq_worker_health_log, minute=set(range(60)), run_at_startup=True)]
    on_startup: StartupShutdown | None = None
    on_shutdown: StartupShutdown | None = None
    redis_settings: RedisSettings | None = _REDIS_SETTINGS
    handle_signals: bool | None = False


@asynccontextmanager
async def arq_lifespan(app: FastAPI) -> AsyncGenerator[Worker]:
    worker = create_worker(
        ArqWorkerSettings,
        ctx={
            EXTERNAL_DEPENDENCIES_CONTEXT_KEY: get_ext_deps_from_app(app),
        },
    )
    task = asyncio.create_task(worker.async_run())

    yield worker

    task.cancel()
    await worker.close()
