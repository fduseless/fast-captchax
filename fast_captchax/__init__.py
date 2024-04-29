import json
from secrets import token_hex
from typing import Annotated, Protocol, Tuple, runtime_checkable
from fastapi import APIRouter, Cookie, Form, Response, status
from pydantic import BaseModel, Field
from datetime import UTC, datetime, timedelta

from .generator import Generator, AsyncGenerator, Captcha
from .store import CapatchStore, AsyncCapatchStore


@runtime_checkable
class Validator(Protocol):
    def __call__(
        self, session_id: str, text: str | None = None, keep_session: bool = False
    ) -> bool: ...


@runtime_checkable
class AsyncValidator(Protocol):
    async def __call__(
        self, session_id: str, text: str | None = None, keep_session: bool = False
    ) -> bool: ...


class CaptchaSession(BaseModel):
    code: str
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    verified: bool = False


DEFAULT_COOKIE_NAME = "_captcha_session_id"
DEFAULT_CAPTCHA_FIELD = "_captcha"
DEFAULT_EXPIRE_MINUTES = 2
SESSION_EXPIRE_DAYS = 1

CAPTCHA_HEADER = {
    "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate",
    "Pragma": "no-cache",
    "Content-Disposition": "inline",
}


def async_captcha(
    generator: AsyncGenerator,
    store: AsyncCapatchStore,
    expire_in: timedelta | None = None,
    captcha_cookie_name: str | None = None,
    captcha_field_name: str | None = None,
) -> Tuple[AsyncValidator, APIRouter]:
    captcha_cookie_name = captcha_cookie_name or DEFAULT_COOKIE_NAME
    captcha_field_name = captcha_field_name or DEFAULT_CAPTCHA_FIELD
    expire_in = expire_in or timedelta(minutes=DEFAULT_EXPIRE_MINUTES)
    session_expire_in = timedelta(SESSION_EXPIRE_DAYS)
    router = APIRouter()

    async def validate(
        session_id: str, text: str | None = None, keep_session: bool = False
    ):
        store_info_str = await store.get(session_id)
        if not keep_session and store_info_str:
            await store.delete(session_id)
        if store_info_str is None:
            return False
        store_info = CaptchaSession(**json.loads(store_info_str))
        if store_info.time + expire_in <= datetime.now(UTC):
            return False
        if not text and store_info.verified:
            return True
        captcha = (text or "").lower().strip()
        if not captcha:
            return False
        if captcha != store_info.code.lower():
            return False
        if keep_session:
            store_info.verified = True
            await store.set(session_id, store_info.model_dump_json())
        return True

    @router.post("/verify", tags=["captcha"])
    async def verify_api(
        text: Annotated[str | None, Form(alias=captcha_field_name)],
        session_id: Annotated[str | None, Cookie(alias=captcha_cookie_name)] = None,
    ):
        _session_id_empty = not session_id
        if _session_id_empty:
            return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        valid = await validate(session_id, text, keep_session=True)
        if not valid:
            await store.delete(session_id)
            return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        return Response(status_code=status.HTTP_200_OK)

    @router.get("/captcha", tags=["captcha"])
    async def captcha_api(
        session_id: Annotated[str | None, Cookie(alias=captcha_cookie_name)] = None
    ):
        _session_id_empty = not session_id
        if _session_id_empty:
            session_id = token_hex(16)
        code, media_type, image_bytes = await generator()
        await store.set(
            session_id, CaptchaSession(code=code).model_dump_json(), ex=expire_in
        )
        response = Response(
            content=image_bytes, media_type=media_type, headers=CAPTCHA_HEADER
        )
        if _session_id_empty:
            response.set_cookie(
                key=captcha_cookie_name,
                value=session_id,
                expires=datetime.now(UTC) + session_expire_in,
            )
        return response

    return validate, router


def captcha(
    generator: Generator,
    store: CapatchStore,
    expire_in: timedelta | None = None,
    captcha_cookie_name: str | None = None,
    captcha_field_name: str | None = None,
) -> Tuple[Validator, APIRouter]:
    captcha_cookie_name = captcha_cookie_name or DEFAULT_COOKIE_NAME
    captcha_field_name = captcha_field_name or DEFAULT_CAPTCHA_FIELD
    expire_in = expire_in or timedelta(minutes=DEFAULT_EXPIRE_MINUTES)
    session_expire_in = timedelta(SESSION_EXPIRE_DAYS)
    router = APIRouter()

    def validate(session_id: str, text: str | None = None, keep_session: bool = False):
        store_info_str = store.get(session_id)
        if not keep_session and store_info_str:
            store.delete(session_id)
        if store_info_str is None:
            return False
        store_info = CaptchaSession(**json.loads(store_info_str))
        if store_info.time + expire_in <= datetime.now(UTC):
            return False
        if not text and store_info.verified:
            return True
        captcha = (text or "").lower().strip()
        if not captcha:
            return False
        if captcha != store_info.code.lower():
            return False
        if keep_session:
            store_info.verified = True
            store.set(session_id, store_info.model_dump_json())
        return True

    @router.get("/verify", tags=["captcha"])
    def verify_api(
        text: Annotated[str | None, Form(alias=captcha_field_name)],
        session_id: Annotated[str | None, Cookie(alias=captcha_cookie_name)] = None,
    ):
        _session_id_empty = not session_id
        if _session_id_empty:
            return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        valid = validate(session_id, text, keep_session=True)
        if not valid:
            store.delete(session_id)
            return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        return Response(status_code=status.HTTP_200_OK)

    @router.get("/captcha", tags=["captcha"])
    def captcha_api(_captcha_session_id: Annotated[str | None, Cookie()] = None):
        _session_id_empty = not _captcha_session_id
        if _session_id_empty:
            _captcha_session_id = token_hex(16)
        code, media_type, image_bytes = generator()
        store.set(
            _captcha_session_id,
            CaptchaSession(code=code).model_dump_json(),
            ex=expire_in,
        )
        response = Response(
            content=image_bytes, media_type=media_type, headers=CAPTCHA_HEADER
        )
        if _session_id_empty:
            response.set_cookie(
                key=captcha_cookie_name,
                value=_captcha_session_id,
                expires=datetime.now(UTC) + session_expire_in,
            )
        return response

    return validate, router
