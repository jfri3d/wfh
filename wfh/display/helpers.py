from datetime import datetime

import requests
from PIL import Image, ImageFont

from wfh.display.constants import API_HOST, FONT
from wfh.display.exceptions import InvalidConnection


def get_today(host: str = API_HOST) -> dict:
    try:
        r = requests.get(f"{host}/today")
        return r.json()["response"]
    except requests.exceptions.ConnectionError as e:
        raise InvalidConnection(str(e))


def build_today(data: dict) -> dict:
    for action, dts in data.items():
        data[action] = [datetime.strptime(dt, "%Y-%m-%d %H:%M:%S") for dt in dts]
    data["now"] = datetime.now()
    return data


def build_font(font_size: int = 12) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, font_size)


def get_font_size(font: ImageFont.FreeTypeFont, text: str) -> (int, int):
    return font.getsize(text)


def load_image(path: str, dy: int) -> Image:
    # open image
    im = Image.open(path)

    # keep aspect ratio
    ratio = im.size[0] / im.size[1]
    im = im.resize((int(ratio * dy), dy), resample=Image.LANCZOS)

    # build appropriate INKY palette
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

    return im.convert("RGB").quantize(palette=pal_img)
