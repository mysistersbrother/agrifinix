import ctypes
from common import WindowInfo, Point

winuser = ctypes.windll.user32


NULL = 0 # Used to match the Win32 API value of "null".

# These FORMAT_MESSAGE_ constants are used for FormatMesage() and are
# documented at https://docs.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-formatmessage#parameters
FORMAT_MESSAGE_ALLOCATE_BUFFER = 0x00000100
FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200


enumWindows = winuser.EnumWindows
enumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
getWindowText = winuser.GetWindowTextW
getWindowTextLength = winuser.GetWindowTextLengthW
show_window = winuser.ShowWindow

SW_SHOWNORMAL = 1
SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_SHOWMINIMIZED = 2

HWND_TOP = 0


SWP_SHOWWINDOW = 0x0040


class Window:
    def __init__(self, hwnd, name):
        self.hwnd = hwnd
        self.name = name


def find_window_with_string(string):
    windows = []

    def foreach_window(hwnd, lParam):
        length = getWindowTextLength(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        getWindowText(hwnd, buffer, length + 1)
        windows.append(Window(hwnd, buffer.value))

    enumWindows(enumWindowsProc(foreach_window), 0)

    for window in windows:
        if string in window.name:
            return window

    return None


def _formatMessage(errorCode):
    """A nice wrapper for FormatMessageW(). TODO

    Microsoft Documentation:
    https://docs.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-formatmessagew

    Additional information:
    https://stackoverflow.com/questions/18905702/python-ctypes-and-mutable-buffers
    https://stackoverflow.com/questions/455434/how-should-i-use-formatmessage-properly-in-c
    """
    lpBuffer = wintypes.LPWSTR()

    ctypes.windll.kernel32.FormatMessageW(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_IGNORE_INSERTS,
                                          NULL,
                                          errorCode,
                                          0, # dwLanguageId
                                          ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR),
                                          0, # nSize
                                          NULL)
    msg = lpBuffer.value.rstrip()
    ctypes.windll.kernel32.LocalFree(lpBuffer) # Free the memory allocated for the error message's buffer.
    return msg


def _raiseWithLastError():
    """A helper function that raises PyGetWindowException using the error
    information from GetLastError() and FormatMessage()."""
    errorCode = ctypes.windll.kernel32.GetLastError()
    raise PyGetWindowException('Error code from Windows: %s - %s' % (errorCode, _formatMessage(errorCode)))


class RECT(ctypes.Structure):
    """A nice wrapper of the RECT structure.

    Microsoft Documentation:
    https://msdn.microsoft.com/en-us/library/windows/desktop/dd162897(v=vs.85).aspx
    """
    _fields_ = [('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)]


class WindowManager:
    def __init__(self, window_name):
        window = find_window_with_string(window_name)

        if window is None:
            raise RuntimeError(f"Could not find any window with the string: {window_name}. Do you have the application open?")
        
        self.window = window

        # initial call required to manipulate later
        # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow
        show_window(window.hwnd, SW_SHOWNORMAL)


    def get_window_info(self) -> WindowInfo:
        window = self.window
        rect = RECT()
        result = winuser.GetWindowRect(window.hwnd, ctypes.byref(rect))
        
        if result == 0:
            _raiseWithLastError()

        print(rect.left)
        print(rect.top)
        print(rect.right)
        print(rect.bottom)

        print(window.name)

        maximised = winuser.IsZoomed(window.hwnd)

        return WindowInfo(
                Point(rect.left, rect.top),
                Point(rect.right, rect.bottom))
#                 maximised)


    def set_window_info(self, window_info: WindowInfo):
        window = self.window

# Could not get minimising/maximising to work - it would always hide the window - maybe don't understand WinApi terminology properly

#         maximised = winuser.IsZoomed(window.hwnd)
#         if window_info.maximised and not maximised:
#             show_window(window.hwnd, SW_MAXIMIZE)
#         else:
#             show_window(window.hwnd, 11) 
#             show_window(window.hwnd, 1)
#             if maximised:
#                 show_window(window.hwnd, 2)
#                 winuser.SetForegroundWindow(window.hwnd)
#                 show_window(window.hwnd, 5)


        left = window_info.top_left.x
        top = window_info.top_left.y
        result = winuser.SetWindowPos(
                window.hwnd,
                HWND_TOP,
                left,
                top,
                window_info.bottom_right.x - left,
                window_info.bottom_right.y - top,
                SWP_SHOWWINDOW)

        if result == 0:
            _raiseWithLastError()

        # show_window(window.hwnd, SW_SHOWNORMAL)



if __name__ == "__main__":
    winManager = WindowManager("Chrome")

    print(winManager.get_window_info().serialize())

    winInfoJson = """
{
    "top_left": {
        "x": 95,
        "y": 50
    },
    "bottom_right": {
        "x": 1768,
        "y": 1120
    },
    "maximised": 0
}"""

    winInfo = WindowInfo.deserialize(winInfoJson)
    print(winInfo)
    winManager.set_window_info(winInfo)

