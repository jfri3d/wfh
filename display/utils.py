from datetime import datetime

import requests
from PIL import Image, ImageDraw, ImageFont
from inky import InkyWHAT

from constants import FONT, TIMES, ICONS, API_HOST

# edge pixel values
X_EDGE = 5
Y_EDGE = 1

# thickness of divider line
DIVIDER_HEIGHT = 4

# footer settings
ICON_SIZE = 30
TICK_HEIGHT = 5

# WFH labels
X_LABEL = 30


def _get_data(host: str = API_HOST):
    r = requests.get(f"{host}/today")
    return r.json()["response"]


def build_data():
    data = _get_data()
    for action, dts in data.items():
        data[action] = [datetime.strptime(dt, "%Y-%m-%d %H:%M:%S") for dt in dts]
    data["now"] = datetime.now()
    return data


def _build_font(font_size: int = 12) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, font_size)


def _get_font_size(font: ImageFont.FreeTypeFont, text: str) -> (int, int):
    return font.getsize(text)


def _load_image(path: str, dy: int) -> Image:
    # open image
    im = Image.open(path)

    # keep aspect ratio
    ratio = im.size[0] / im.size[1]
    im = im.resize((int(ratio * dy), dy), resample=Image.LANCZOS)

    # build appropriate INKY palette
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

    return im.convert("RGB").quantize(palette=pal_img)


# TODO -> remove!??
def _clean_inky(inky):
    # draw empty image
    img = Image.new("P", (inky.WIDTH, inky.HEIGHT))
    inky.set_image(img)
    return inky


def _convert_time(date: datetime, start_px: int, end_px: int, start_hr: int = 8, total_time: int = 12) -> int:
    dpx_dsec = (end_px - start_px) / (total_time * 60 * 60)
    dsec = (date - datetime(date.year, date.month, date.day, start_hr)).total_seconds()
    px = start_px + int(dsec * dpx_dsec) + 1  # weird the +1 is necessary...
    return max([start_px, min([px, end_px])])


def update_inky():
    data = build_data()
    print(data)

    # INIT
    # ====
    inky = InkyWHAT("yellow")
    inky.set_border(inky.BLACK)

    # initiate image
    img = Image.new("P", (inky.WIDTH, inky.HEIGHT))
    draw = ImageDraw.Draw(img)

    # HEADER
    # ======

    # add name
    x = "WFH"
    font = _build_font(20)
    w, h = _get_font_size(font, x)
    draw.text((X_EDGE, Y_EDGE), x, inky.YELLOW, font)

    # add date
    now = data["now"]
    date_str = now.strftime("%d.%m.%Y")
    wd, _ = _get_font_size(font, date_str)
    time_str = now.strftime("%H:%M")
    wt, _ = _get_font_size(font, time_str)

    draw.text((inky.WIDTH - wt - wd - X_EDGE, Y_EDGE), date_str, inky.BLACK, font)
    draw.text((inky.WIDTH - wt, Y_EDGE), time_str, inky.YELLOW, font)

    # add divider
    HEADER_HEIGHT = h + Y_EDGE
    draw.line((X_EDGE, HEADER_HEIGHT + 2, inky.WIDTH - X_EDGE, HEADER_HEIGHT + 2), fill=inky.BLACK,
              width=DIVIDER_HEIGHT)

    # FOOTER
    # ======
    TIME_END = inky.WIDTH - 2 * X_EDGE
    dx = (TIME_END - X_LABEL) // len(TIMES)

    x = X_LABEL + X_EDGE
    y = inky.HEIGHT - ICON_SIZE * 1.5

    # determine absolute start/end time (for referencing)
    TIME_START = x + (dx + ICON_SIZE) // 2
    TIME_END -= ICON_SIZE // 2 - X_EDGE

    # add ENTIRE time bar
    draw.line((TIME_START, y, TIME_END, y), fill=inky.BLACK, width=DIVIDER_HEIGHT)

    # add icons
    for k, v in TIMES.items():
        icon = _load_image(v, ICON_SIZE)

        # add icons
        img.paste(icon, box=(x + dx // 2, inky.HEIGHT - ICON_SIZE - 2 * Y_EDGE))

        # add MAJOR time ticks
        draw.line((x + (dx + ICON_SIZE) // 2, y + TICK_HEIGHT, x + (dx + ICON_SIZE) // 2, y - TICK_HEIGHT),
                  fill=inky.BLACK, width=int(1.25 * DIVIDER_HEIGHT))
        # add MINOR time ticks
        draw.line((x + dx + ICON_SIZE // 2, y + TICK_HEIGHT, x + dx + ICON_SIZE // 2, y - TICK_HEIGHT),
                  fill=inky.BLACK, width=int(0.75 * DIVIDER_HEIGHT))
        x += dx

    now_px = _convert_time(data["now"], TIME_START, TIME_END)
    draw.line((now_px, y + TICK_HEIGHT, now_px, y - TICK_HEIGHT),
              fill=inky.YELLOW,
              width=int(1.25 * DIVIDER_HEIGHT))

    # WORK
    # ====

    Y = 60

    # add label
    label = "Work"
    font = _build_font(30)
    w, h = _get_font_size(font, label[0])
    draw.text((X_EDGE + w, Y - h // 2), label[1:], inky.BLACK, font)
    draw.text((X_EDGE, Y - h // 2), label[0], inky.YELLOW, font)

    # fix logoff if not existing
    if len(data["login"]) != len(data["logoff"]):
        data["logoff"].append(data["now"])
    working_times = list(zip(data["login"], data["logoff"]))

    total_sec = 0
    font = _build_font(18)
    for working_time in working_times:
        # start
        start_px = _convert_time(working_time[0], TIME_START, TIME_END)
        start_str = working_time[0].strftime("%H:%M")
        draw.text((start_px, Y + 4), start_str, inky.BLACK, font)

        # end
        stop_px = _convert_time(working_time[1], TIME_START, TIME_END)
        if (stop_px - start_px) > 100:
            stop_str = working_time[1].strftime("%H:%M")
            w, h = _get_font_size(font, stop_str)
            draw.text((stop_px - int(0.75 * w), Y + 4), stop_str, inky.BLACK, font)

        # total
        total_sec += (working_time[1] - working_time[0]).total_seconds()

        # add time bar for working time
        draw.line((start_px, Y, stop_px, Y), fill=inky.YELLOW, width=3 * DIVIDER_HEIGHT)

    # write total work time
    total_str = "Σ {:.2f} hr".format(total_sec / 3600)
    font = _build_font(25)
    w, h = _get_font_size(font, total_str)
    draw.text((inky.WIDTH - w - X_EDGE, HEADER_HEIGHT + 5), total_str, inky.YELLOW, font)

    # FOOD
    # ====

    Y = 125

    # add label
    label = "Food"
    font = _build_font(30)
    w, h = _get_font_size(font, label[0])
    draw.text((2 * X_EDGE + w // 3, Y - h // 2), label[1:], inky.BLACK, font)
    draw.text((X_EDGE, Y - h // 2), label[0], inky.YELLOW, font)

    # add lunch icon
    if data["lunch"]:
        icon = _load_image(ICONS["lunch"], ICON_SIZE)
        lunch_px = _convert_time(data["lunch"][0], TIME_START, TIME_END)  # ASSUME SINGLE LUNCH
        img.paste(icon, box=(lunch_px - ICON_SIZE // 2, Y - ICON_SIZE))

    # add coffee icons
    for coffee in data["coffee"]:
        icon = _load_image(ICONS["coffee"], ICON_SIZE)
        coffee_px = _convert_time(coffee, TIME_START, TIME_END)
        img.paste(icon, box=(coffee_px - ICON_SIZE // 2, Y + ICON_SIZE // 3))

    # FOOD
    # ====

    Y = 205

    # add label
    label = "Health"
    font = _build_font(30)
    w, h = _get_font_size(font, label[0])
    draw.text((X_EDGE + w, Y - h // 2), label[1:], inky.BLACK, font)
    draw.text((X_EDGE, Y - h // 2), label[0], inky.YELLOW, font)

    # add pushup icons
    for pushups in data["pushups"]:
        icon = _load_image(ICONS["pushups"], ICON_SIZE)
        pushups_px = _convert_time(pushups, TIME_START, TIME_END)
        img.paste(icon, box=(pushups_px - ICON_SIZE // 2, Y - ICON_SIZE))

    # add move icons
    for move in data["move"]:
        icon = _load_image(ICONS["move"], ICON_SIZE)
        move_px = _convert_time(move, TIME_START, TIME_END)
        img.paste(icon, box=(move_px - ICON_SIZE // 2, Y + ICON_SIZE // 3))

    # set image to inky
    inky.set_image(img)
    inky.show()
