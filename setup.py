from window_manager import WindowManager
from pixel_helper import get_indicators
from common import Settings, SETTINGS_FILENAME 

print("Finding Roblox window...")

windowManager = WindowManager("Roblox")

print("The macro needs to run on a consistent window size. If you would like to use a smaller window size, please change the window size to your preference now. These will be saved and then the macro will resize the window at the start of every run.")
print("When you have resized the window and are ready to continue, press enter in the terminal")
print("Note: If you are using fullscreen or maximised windows, make sure to maximise/full screen the Roblox window before using the macro, the macro will not do this for you.")
print()
print("Press Enter when you are ready")

input()

# Must come before get_indicators which will set dpi awareness due to mss
window_info = windowManager.get_window_info()

print("Now we need to collect the position of indicators which the macro uses to determine where the fish is.")
print("Please start fishing and as soon as the minigame begins then click Enter in the terminal.")
input()

indicators = get_indicators()

settings = Settings(window_info, indicators)

with open(SETTINGS_FILENAME, "w+") as f:
  f.write(settings.serialize())

