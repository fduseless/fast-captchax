# Fast CaptchaX

Captcha Validator for FastAPI

## Install

```bash
pip install fast_captchax
```

## Usage

### sync version

```python
from datetime import timedelta
from fastapi import FastAPI
from fast_captchax import captcha
from fast_captchax.memory import MemoryCapatchStore
from fast_captchax.redis import RedisCapatchStore
from captchax import create_image

validate, captcha_router = captcha(
    generator = CaptchaXGenerator(),
    store = MemoryCapatchStore(), # memory captcha store is only used for test. please use RedisCapatchStore in production
    expire_in = timedelta(minutes=2), # by default is 2 minutes
    captcha_cookie_name = None, # by default _captcha_session_id
    captcha_field_name = None, # verify api form field, by default _captcha
)

app = FastAPI()
app.include_router(captcha_router, prefix="/api")
```

in your form

```html
<form>
  <img
    alt="Captcha"
    name="_captcha"
    src="/api/captcha/"
    onclick="this.src = '/api/captcha/?t=' + Date.now();"
  />
</form>
```

You can check your captcha in JS for better user experience.

```javascript
let formData = new FormData();
formData.append("_captcha", "user input captcha");
resp = await fetch("/api/verify", { body: formData });
resp.status == 200; // if captcha is correct
resp.status == 429; // if captcha is incorrect, Please refresh captcha.
```

check in your server

```python
from fastapi import Response, status
@app.get("/your_api")
def api(user_input=Annotated[str | None, Form(alias="_captcha")],
    session: Annotated[str | None, Cookie(alias="_captcha")] = None):
    if validate(session, user_input):
        return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
```

if you have called verify API previously.

```python
from fastapi import Response, status
@app.get("/your_api")
def api(session: Annotated[str | None, Cookie(alias="_captcha")] = None):
    if validate(session):
        return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
```

We also provide async version.

Please use

```python
from datetime import timedelta
from fastapi import FastAPI
from fast_captchax import async_captcha
from captchax import create_image
from fast_captchax.memory import AsyncMemoryCapatchStore
from fast_captchax.redis import AsyncRedisCapatchStore

async def async_create_image():
    return await asyncio.to_thread(CaptchaXGenerator())

validate, captcha_router = async_captcha(
    generator = async_create_image,
    store = AsyncMemoryCapatchStore(), # memory captcha store is only used for test. please use RedisCapatchStore in production
    expire_in = timedelta(minutes=2), # by default is 2 minutes
    captcha_cookie_name = None, # by default _captcha_session_id
    captcha_field_name = None, # verify api form field, by default _captcha
)

app = FastAPI()
app.include_router(captcha_router, prefix="/api")
```

check in your server.

```python
from fastapi import Response, status
@app.get("/your_api")
async def api(user_input=Annotated[str | None, Form(alias="_captcha")],
    session: Annotated[str | None, Cookie(alias="_captcha")] = None):
    if await validate(session, user_input):
        return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
```

if you have called verify API previously.

```python
from fastapi import Response, status
@app.get("/your_api")
async def api(session: Annotated[str | None, Cookie(alias="_captcha")] = None):
    if await validate(session):
        return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
```

## Example

```bash
poetry run uvicorn example:app
```
