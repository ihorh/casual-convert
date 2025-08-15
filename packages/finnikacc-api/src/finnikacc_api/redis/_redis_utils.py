from collections.abc import AsyncIterable, Awaitable

from redis.asyncio import Redis
from redis.typing import ExpiryT


async def _redis_await[T](coro: Awaitable[T] | T) -> T:
    if not isinstance(coro, Awaitable):
        msg = "expect async redis client here."
        raise TypeError(msg)

    return await coro


async def hsetex(
    redis: Redis,
    name: str,
    mapping: dict[str, str] | None = None,
    ex: ExpiryT | None = None,
) -> int:
    result = await _redis_await(redis.hset(name=name, mapping=mapping))
    if ex:
        await redis.expire(name, ex)
    return result


async def _hgetall_names(redis: Redis, names: AsyncIterable[str]) -> list[dict[bytes, bytes]]:
    async with redis.pipeline() as pipe:
        async for k in names:
            pipe.hgetall(k)
        return await pipe.execute()
