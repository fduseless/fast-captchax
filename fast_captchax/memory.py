from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from queue import PriorityQueue
import threading
import asyncio


# only for test


@dataclass(order=True)
class ExpireKey:
    priority: datetime
    item: str = field(compare=False)


class MemoryCapatchStore:
    def __init__(self) -> None:
        self._data = {}
        self._expire = PriorityQueue()
        self._lock = threading.Lock()

    def remove_expired(self):
        now = datetime.now(UTC)
        while not self._expire.empty():
            item = self._expire.queue[0]
            if item.priority >= now:
                k = self._expire.get()
                if k in self._data:
                    del self._data[k]
            else:
                break

    def expire(self, ex: None | int | timedelta = None) -> datetime | None:
        expire = None
        if isinstance(ex, float):
            expire = datetime.now(UTC) + timedelta(seconds=ex)
        elif isinstance(ex, timedelta):
            expire = datetime.now(UTC) + ex
        return expire

    def set(
        self, name: str, value: str, ex: None | int | timedelta = None
    ) -> bool | None:
        try:
            self._lock.acquire()
            self.remove_expired()
            expire = self.expire(ex)
            self._data[name] = (value, expire)
            if expire is not None:
                self._expire.put(ExpireKey(expire, name))
        finally:
            self._lock.release()

    def get(self, name: str) -> str | None:
        try:
            self._lock.acquire()
            self.remove_expired()
            ret = self._data.get(name)
            if ret:
                return ret[0]
            return None
        finally:
            self._lock.release()

    def delete(self, name: str) -> None:
        try:
            self._lock.acquire()
            self.remove_expired()
            if name in self._data:
                del self._data[name]
        finally:
            self._lock.release()


class AsyncMemoryCapatchStore:
    def __init__(self) -> None:
        self._data = {}
        self._expire = PriorityQueue()
        self._lock = asyncio.Lock()

    def remove_expired(self):
        now = datetime.now(UTC)
        while not self._expire.empty():
            item = self._expire.queue[0]
            if item.priority >= now:
                self._expire.get()
            else:
                break

    def expire(self, ex: None | float | timedelta = None) -> datetime | None:
        expire = None
        if isinstance(ex, float):
            expire = datetime.now(UTC) + timedelta(seconds=int(ex))
        elif isinstance(ex, timedelta):
            expire = datetime.now(UTC) + ex
        return expire

    async def set(
        self, name: str, value: str, ex: None | float | timedelta = None
    ) -> bool | None:
        try:
            await self._lock.acquire()
            self.remove_expired()
            expire = self.expire(ex)
            self._data[name] = (value, expire)
            if expire is not None:
                self._expire.put(ExpireKey(expire, name))
        finally:
            self._lock.release()

    async def get(self, name: str) -> str | None:
        try:
            await self._lock.acquire()
            self.remove_expired()
            ret = self._data.get(name)
            if ret:
                return ret[0]
            return None
        finally:
            self._lock.release()

    async def delete(self, name: str) -> None:
        try:
            await self._lock.acquire()
            self.remove_expired()
            if name in self._data:
                del self._data[name]
        finally:
            self._lock.release()
