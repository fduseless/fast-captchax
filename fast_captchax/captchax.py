from .generator import Captcha
from captchax import create_image  # type: ignore


class CaptchaXGenerator:
    def __call__(self) -> Captcha:
        code, image = create_image()
        return (code, "png", image)
