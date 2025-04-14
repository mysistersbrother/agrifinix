import cv2
import mss
import numpy as np
from common import IndicatorInfo, Point

coords = []
instructions_list = [
    "Please click in the middle of a letter from the 'Fish!' text, the point should be surrounded by white.",
    "Click on the top of the blue fishing box, just below the 'Fish!' text.",
    "Now click on the bottom of the blue fishing box.",
    "Click on the top of the green/red fishing bar.",
    "Now click on the bottom of the green/red fishing bar.",
    "Carefully click in the middle of the black fish eye."

]


def update_display(base_image, instruction):
    display = base_image.copy()

    cv2.rectangle(display, (0, 0), (display.shape[1], 40), (255, 255, 255), -1)

    cv2.putText(display, instruction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 0, 0), 2, cv2.LINE_AA)

    for i, pt in enumerate(coords):
        cv2.circle(display, pt, 6, (0, 0, 255), -1)

    cv2.imshow("Image", display)


def click_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        coords.append((x, y))

        if len(coords) < len(instructions_list):
            new_text = instructions_list[len(coords)]
        else:
            new_text = "Done! You can press any key to continue."

        update_display(param["original"], new_text)



def get_indicators() -> IndicatorInfo:
    sct = mss.mss()
    primary_monitor = sct.monitors[0]
    img = sct.grab(primary_monitor)

    coords.clear()

    np_img = np.array(img)
    cv2_img = cv2.cvtColor(np_img, cv2.COLOR_RGBA2RGB)

    update_display(cv2_img, instructions_list[0])

    cv2.setMouseCallback("Image", click_callback, {"original": cv2_img})
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    expected_points = len(instructions_list)

    if len(coords) != expected_points:
        raise RuntimeError(f"Expected {expected_points} points but got {len(coords)}. Please follow all the instructions and then click any key to exit the window.")

    return IndicatorInfo(
            coords[1][1],
            coords[2][1],
            Point(coords[5][0], coords[5][1]),
            coords[3][1],
            coords[4][1],
            Point(coords[0][0], coords[0][1]))


if __name__ == "__main__":
    indicators = get_indicators()

    print(indicators)
