import pytest
import pytest_asyncio
import redis.asyncio as redis
from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from arq import ArqRedis
from finnikacc_api import settings
from finnikacc_api.arqjobs.fetchrates import fetch_conv_rates_oex
from finnikacc_api.lifecycle.dependencies import EXTERNAL_DEPENDENCIES_CONTEXT_KEY, ExternalDependencies


@pytest_asyncio.fixture(scope="module")
async def external_dependencies():
    deps = ExternalDependencies(
        redis=redis.Redis(),
        arq_redis=ArqRedis(),
        oex_client=CachedSession(
            settings.app.OEX_RATES_BASE_URL,
            headers={"Authorization": f"Token {settings.secret.OEX_RATES_APP_ID}"},
            allow_redirects=False,
            cache=SQLiteBackend(
                settings.app.OEX_CACHE_DB_NAME,
                expire_after=settings.app.OEX_CACHE_EXPIRE_AFTER_SEC,
            ),
        ),
    )
    yield deps

    await deps.oex_client.close()

@pytest.mark.asyncio(scope="module")
async def test_fetchrates(external_dependencies: ExternalDependencies):
    await fetch_conv_rates_oex({EXTERNAL_DEPENDENCIES_CONTEXT_KEY: external_dependencies})
