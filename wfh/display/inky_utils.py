from datetime import datetime

from PIL import Image, ImageDraw
from inky import InkyWHAT

from wfh.display.constants import TIMES, ICONS
from wfh.display.helpers import get_today, build_today, build_font, get_font_size, load_image

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
    raw = get_today()
    data = build_today(raw)
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
    font = build_font(20)
    w, h = get_font_size(font, x)
    draw.text((X_EDGE, Y_EDGE), x, inky.YELLOW, font)

    # add date
    now = data["now"]
    date_str = now.strftime("%d.%m.%Y")
    wd, _ = get_font_size(font, date_str)
    time_str = now.strftime("%H:%M")
    wt, _ = get_font_size(font, time_str)

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
        icon = load_image(v, ICON_SIZE)

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
    font = build_font(30)
    w, h = get_font_size(font, label[0])
    draw.text((X_EDGE + w, Y - h // 2), label[1:], inky.BLACK, font)
    draw.text((X_EDGE, Y - h // 2), label[0], inky.YELLOW, font)

    # fix logoff if not existing
    if len(data["login"]) != len(data["logoff"]):
        data["logoff"].append(data["now"])
    working_times = list(zip(data["login"], data["logoff"]))

    total_sec = 0
    font = build_font(18)
    for working_time in working_times:
        # start
        start_px = _convert_time(working_time[0], TIME_START, TIME_END)
        start_str = working_time[0].strftime("%H:%M")
        draw.text((start_px, Y + 4), start_str, inky.BLACK, font)

        # end
        stop_px = _convert_time(working_time[1], TIME_START, TIME_END)
        if (stop_px - start_px) > 100:
            stop_str = working_time[1].strftime("%H:%M")
            w, h = get_font_size(font, stop_str)
            draw.text((stop_px - int(0.75 * w), Y + 4), stop_str, inky.BLACK, font)

        # total
        total_sec += (working_time[1] - working_time[0]).total_seconds()

        # add time bar for working time
        draw.line((start_px, Y, stop_px, Y), fill=inky.YELLOW, width=3 * DIVIDER_HEIGHT)

    # write total work time
    total_str = "Σ {:.2f} hr".format(total_sec / 3600)
    font = build_font(25)
    w, h = get_font_size(font, total_str)
    draw.text((inky.WIDTH - w - X_EDGE, HEADER_HEIGHT + 5), total_str, inky.YELLOW, font)

    # FOOD
    # ====

    Y = 128

    # add label
    label = "Food"
    font = build_font(30)
    w, h = get_font_size(font, label[0])
    draw.text((2 * X_EDGE + w // 3, Y - h // 2), label[1:], inky.BLACK, font)
    draw.text((X_EDGE, Y - h // 2), label[0], inky.YELLOW, font)

    # add lunch icon
    if data["lunch"]:
        icon = load_image(ICONS["lunch"], int(ICON_SIZE * .75))
        lunch_px = _convert_time(data["lunch"][0], TIME_START, TIME_END)  # ASSUME SINGLE LUNCH
        img.paste(icon, box=(lunch_px, Y - ICON_SIZE))

    # add coffee icons
    for coffee in data["coffee"]:
        icon = load_image(ICONS["coffee"], ICON_SIZE)
        coffee_px = _convert_time(coffee, TIME_START, TIME_END)
        img.paste(icon, box=(coffee_px - ICON_SIZE // 2, Y + ICON_SIZE // 3))

    # HEALTH
    # ======

    Y = 205

    # add label
    label = "Health"
    font = build_font(30)
    w, h = get_font_size(font, label[0])
    draw.text((X_EDGE + w, Y - h // 2), label[1:], inky.BLACK, font)
    draw.text((X_EDGE, Y - h // 2), label[0], inky.YELLOW, font)

    # add pushup icons
    for pushups in data["pushups"]:
        icon = load_image(ICONS["pushups"], ICON_SIZE)
        pushups_px = _convert_time(pushups, TIME_START, TIME_END)
        img.paste(icon, box=(pushups_px - ICON_SIZE // 2, Y - ICON_SIZE))

    # add move icons
    for move in data["move"]:
        icon = load_image(ICONS["move"], ICON_SIZE)
        move_px = _convert_time(move, TIME_START, TIME_END)
        img.paste(icon, box=(move_px - ICON_SIZE // 2, Y + ICON_SIZE // 3))

    # set image to inky
    inky.set_image(img)
    inky.show()
