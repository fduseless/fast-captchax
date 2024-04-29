from typing import Protocol, Tuple, runtime_checkable


Captcha = Tuple[str, str, bytes]


@runtime_checkable
class Generator(Protocol):
    def __call__(
        self,
    ) -> Captcha: ...


@runtime_checkable
class AsyncGenerator(Protocol):
    async def __call__(
        self,
    ) -> Captcha: ...
