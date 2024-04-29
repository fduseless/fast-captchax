from typing import cast
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from datetime import timedelta


class RedisCapatchStore:
    def __init__(self, rc: Redis) -> None:
        self._rc = rc

    def set(
        self, name: str, value: str, ex: None | int | timedelta = None
    ) -> bool | None:
        return cast(bool | None, self._rc.set(name, value, ex=ex))

    def get(self, name: str) -> str | None:
        ret = cast(bytes | None, self._rc.get(name))
        if ret is not None:
            return ret.decode("utf8")
        return ret

    def delete(self, name: str) -> None:
        self._rc.delete(name)


class AsyncRedisCapatchStore:
    def __init__(self, rc: AsyncRedis) -> None:
        self._rc = rc

    async def set(
        self, name: str, value: str, ex: None | int | timedelta = None
    ) -> bool | None:
        return await self._rc.set(name, value, ex=ex)

    async def get(self, name: str) -> str | None:
        ret = await self._rc.get(name)
        if ret is not None:
            return ret.decode("utf8")
        return ret

    async def delete(self, name: str) -> None:
        await self._rc.delete(name)
