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
from finnikacc_api.arqjobs.arq_jobs import arq_cron_jobs, arq_functions
from finnikacc_api.lifecycle.dependencies import (
    EXTERNAL_DEPENDENCIES_CONTEXT_KEY,
    INTERNAL_DEPENDENCIES_CONTEXT_KEY,
    get_ext_deps_from_app,
    get_int_deps_from_app,
)

LOG = logging.getLogger(__name__)


async def _arq_worker_health_log(ctx: dict) -> None:  # noqa: ARG001
    LOG.debug("arq worker health check log: ")


_REDIS_SETTINGS = RedisSettings(
    host=settings.app.REDIS_HOST,
    port=settings.app.REDIS_PORT,
    database=int(settings.app.REDIS_DB),
)


class ArqWorkerSettings:
    functions: Sequence[WorkerCoroutine | Function] = arq_functions
    cron_jobs: Sequence[CronJob] | None = [
        cron(_arq_worker_health_log, minute=set(range(60)), run_at_startup=True),
        *arq_cron_jobs,
    ]
    on_startup: StartupShutdown | None = None
    on_shutdown: StartupShutdown | None = None
    redis_settings: RedisSettings | None = _REDIS_SETTINGS
    handle_signals: bool | None = False


def _context_from_app_state(app: FastAPI) -> dict:
    return {
        EXTERNAL_DEPENDENCIES_CONTEXT_KEY: get_ext_deps_from_app(app),
        INTERNAL_DEPENDENCIES_CONTEXT_KEY: get_int_deps_from_app(app),
    }


@asynccontextmanager
async def arq_lifespan(app: FastAPI) -> AsyncGenerator[Worker]:
    worker = create_worker(ArqWorkerSettings, ctx=_context_from_app_state(app))
    task = asyncio.create_task(worker.async_run())

    yield worker

    task.cancel()
    await worker.close()
