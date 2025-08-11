from typing import cast

from redis.asyncio import Redis

from finnikacc_api import settings
from finnikacc_api.redis._redis_utils import _redis_await, hsetex
from finnikacc_api.redis.model import (
    CurrencyRateCacheType,
    CurrencyRateCacheValue,
    CurrencyRateCacheValueTyped,
    RequestLastModETagCacheValue,
    RequestLastModETagCacheValueTyped,
    _convert_to_typed_etag,
    _convert_to_untyped_cr,
    _convert_to_untyped_etag,
)

last_request = "fcc:prod_render:provider:oex:request:latest"
last_request_value = {"last_modified", "ETag"}


class LastRequestETagRedisCache:
    def __init__(
        self,
        redis: Redis,
        *,
        expiration_seconds: int,
        namespace: str = "fcc",
        provider: str = "oex",
    ) -> None:
        self._redis = redis
        self._ex = expiration_seconds
        self._name_prefix = f"{namespace}:{settings.APP_ENV}:last_request:{provider}"
        self._name_template = f"{self._name_prefix}:{{endpoint}}"

    def _name(self, endpoint: str) -> str:
        return self._name_template.format(endpoint=endpoint)

    async def hget_conv(self, endpoint: str) -> RequestLastModETagCacheValueTyped | None:
        result = await self.hget_raw(endpoint)
        return _convert_to_typed_etag(result) if result else None

    async def hget_raw(self, endpoint: str) -> RequestLastModETagCacheValue | None:
        result: dict[bytes, bytes] = await _redis_await(self._redis.hgetall(self._name(endpoint)))
        if not result:
            return None
        return cast("RequestLastModETagCacheValue", {k.decode(): v.decode() for k, v in result.items()})

    async def hset_conv(self, mapping: RequestLastModETagCacheValueTyped, *, endpoint: str) -> None:
        await self.hset_raw(_convert_to_untyped_etag(mapping), endpoint=endpoint)

    async def hset_raw(self, mapping: RequestLastModETagCacheValue, *, endpoint: str) -> None:
        async with self._redis.pipeline() as pipe:
            await hsetex(
                pipe,
                name=self._name(endpoint),
                mapping=cast("dict[str, str]", mapping),
                ex=self._ex,
            )


class CurrencyRateRedisCache:
    def __init__(
        self,
        redis: Redis,
        *,
        expiration_seconds: int,
        namespace: str = "fcc",
        provider: str = "oex",
        cache_type: CurrencyRateCacheType,
    ) -> None:
        self._redis = redis
        self._ex = expiration_seconds
        self._name_prefix = f"{namespace}:{settings.APP_ENV}:rates:{provider}:{cache_type}"
        self._name_template = f"{self._name_prefix}:{{base_currency}}:{{quote_currency}}"

    def _name(self, base_currency: str, quote_currency: str) -> str:
        return self._name_template.format(base_currency=base_currency, quote_currency=quote_currency)

    async def hset_conv(self, mapping: CurrencyRateCacheValueTyped, *, base_currency: str, quote_currency: str) -> None:
        await self.hset_raw(_convert_to_untyped_cr(mapping), base_currency=base_currency, quote_currency=quote_currency)

    async def hset_raw(self, mapping: CurrencyRateCacheValue, *, base_currency: str, quote_currency: str) -> None:
        await _redis_await(
            self._redis.hsetex(
                name=self._name(base_currency, quote_currency),
                mapping=cast("dict[str, str]", mapping),
                ex=self._ex,
            ),
        )

    async def hset_m_conv(self, mappings: dict[str, CurrencyRateCacheValueTyped], *, base_currency: str) -> None:
        mappings_un = {k: _convert_to_untyped_cr(v) for k, v in mappings.items()}
        await self.hset_m_raw(mappings_un, base_currency=base_currency)

    async def hset_m_raw(self, mappings: dict[str, CurrencyRateCacheValue], *, base_currency: str) -> None:
        async with self._redis.pipeline() as pipe:
            for q_curr, mapping in mappings.items():
                await hsetex(
                    pipe,
                    name=self._name(base_currency, q_curr),
                    mapping=cast("dict[str, str]", mapping),
                    ex=self._ex,
                )
            await pipe.execute()
