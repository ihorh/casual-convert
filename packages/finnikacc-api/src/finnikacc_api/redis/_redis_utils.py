from collections.abc import Awaitable


async def _redis_await[T](coro: Awaitable[T] | T) -> T:
    if not isinstance(coro, Awaitable):
        msg = "expect async redis client here."
        raise TypeError(msg)

    return await coro
