from time import sleep, time
from window_manager import WindowManager
from mss import mss
from directKeys import click_anywhere, queryMousePosition
from common import Settings, SETTINGS_FILENAME 
import os.path


def load_settings():
    if not os.path.isfile(SETTINGS_FILENAME):
        return None

    with open(SETTINGS_FILENAME) as f:
        return Settings.deserialize(f.read())


class ColourGrabber:
    def __init__(self, sct):
        self.bbox = {"left": 0, "top": 0, "width": 1, "height": 1}
        self.sct = sct

    def close(self):
        self.sct.close()

    def grab_pixel(self, x, y):
        self.bbox["left"] = x
        self.bbox["top"] = y

        return self.sct.grab(self.bbox).pixel(0, 0)


def all(iterable, cond):
    for item in iterable:
        if not cond(item):
            return False
    return True


def is_white(pixel):
    return all(pixel, lambda colour: colour > 230)


def is_black(pixel):
    return all(pixel, lambda colour: colour < 5)


def is_green(pixel):
    return 65 <= pixel[0] <= 75 and 165 <= pixel[1] <= 180 and 95 < pixel[2] <= 110


def is_red(pixel):
    return 130 < pixel[0] <= 160 and 60 < pixel[1] <= 80 and 85 <= pixel[2] <= 100


def is_bar(pixel):
    return is_green(pixel) or is_red(pixel)


settings = load_settings()

if settings is None:
    print("Could not load settings.json, have you run the setup.py script as per the instructions?")
    exit()


window_info = settings.window
windowManager = WindowManager("Roblox")
windowManager.set_window_info(window_info)

# This must go after SetWindowInfo because it has side effects (setting dpi awareness) which messes with the pixel values
sct = mss()

grabber = ColourGrabber(sct)

indicators = settings.indicators

top_box = indicators.top_box
bottom_box = indicators.bottom_box
height = bottom_box - top_box

middle = indicators.fish_eye.x

bar_top = indicators.bar_top
bar_bottom = indicators.bar_bottom
bar_height = bar_bottom - bar_top
half_bar_height = bar_height / 2

line_box = {"left": middle, "top": top_box, "width": 1, "height": height}

sleep(2)

fish_text = indicators.fish_text
x = fish_text.x
y = fish_text.y

isFishing = is_white(grabber.grab_pixel(x, y))

if isFishing:
    print("Currently fishing...")
else:
    print("Not currently fishing...")


def is_fishing():
    return is_white(grabber.grab_pixel(x, y))


POLL_PERIOD = 0.02
CLICK_TIME = 0.08

while True:
    if not is_fishing():
        print("not fishing...")

        sleep(POLL_PERIOD)
        continue

    print("fishing...")

    line = sct.grab(line_box)

    found = False

    fish_y = None
    bar_y = None

    for i in range(height):
        pix = line.pixel(0, i)
        if is_black(pix):
            fish_y = i
            print(f"Found fish at y: {i}")
        elif bar_y is None and is_bar(pix):
            bar_y = i
            print(f"Found bar at y: {i}")

        if fish_y is not None and bar_y is not None:
            found = True
            break

    if not found:
        print("Could not find fish or bar")
        continue

    bar_y_normalized = bar_y + half_bar_height + (50 - half_bar_height) * (bar_y <= 90)
    distance = bar_y_normalized - fish_y
    if distance > 0:
        print(f"adjusting (click, distance: {distance})")
        click_time = CLICK_TIME + (CLICK_TIME * (distance > 100))
        print(f"click time: {click_time}")
        click_anywhere(click_time)
    else:
        print("adjusting (no click)")

    sleep(POLL_PERIOD)

