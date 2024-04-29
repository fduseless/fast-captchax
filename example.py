import asyncio
from datetime import timedelta

from fastapi import FastAPI
from fast_captchax import captcha
from fast_captchax.memory import MemoryCapatchStore
from fast_captchax.redis import RedisCapatchStore
from fast_captchax.captchax import CaptchaXGenerator

from fast_captchax import async_captcha
from fast_captchax.memory import AsyncMemoryCapatchStore
from fast_captchax.redis import AsyncRedisCapatchStore

validate, captcha_router = captcha(
    generator=CaptchaXGenerator(),
    store=MemoryCapatchStore(),  # memory captcha store is only used for test. please use RedisCapatchStore in production
    expire_in=timedelta(minutes=2),  # by default is 2 minutes
    captcha_cookie_name=None,  # by default _captcha_session_id
    captcha_field_name=None,  # verify api form field, by default _captcha
)

app = FastAPI()
app.include_router(captcha_router, prefix="/api")


async def async_create_image():
    return await asyncio.to_thread(CaptchaXGenerator())


validate, captcha_router = async_captcha(
    generator=async_create_image,
    store=AsyncMemoryCapatchStore(),  # memory captcha store is only used for test. please use RedisCapatchStore in production
    expire_in=timedelta(minutes=2),  # by default is 2 minutes
    captcha_cookie_name=None,  # by default _captcha_session_id
    captcha_field_name=None,  # verify api form field, by default _captcha
)

app = FastAPI()
app.include_router(captcha_router, prefix="/api")
