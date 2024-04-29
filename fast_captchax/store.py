from datetime import timedelta
from typing import Protocol, runtime_checkable


@runtime_checkable
class CapatchStore(Protocol):
    def set(
        self, name: str, value: str, ex: None | int | timedelta = None
    ) -> bool | None: ...
    def get(self, name: str) -> str | None: ...
    def delete(self, name: str) -> None: ...


@runtime_checkable
class AsyncCapatchStore(Protocol):
    async def set(
        self, name: str, value: str, ex: None | int | timedelta = None
    ) -> bool | None: ...
    async def get(self, name: str) -> str | None: ...
    async def delete(self, name: str) -> None: ...
