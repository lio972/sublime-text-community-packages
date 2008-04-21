import ctypes
from ctypes import windll

def enum_windows():
    windows = []
    def EnumWindowProc(hwnd, lparam):
        windows.append(hwnd)
        return True
    enum_win_proc = ctypes.WINFUNCTYPE(
        ctypes.c_int, ctypes.c_long, ctypes.c_long)

    proc = enum_win_proc(EnumWindowProc)
    windll.user32.EnumWindows(proc, 0)
    return windows

def classname(handle):
    class_name = (ctypes.c_wchar * 257)()
    windll.user32.GetClassNameW(handle, ctypes.byref(class_name), 256)
    return class_name.value

def text(handle):
    length = windll.user32.GetWindowTextLengthW(handle,)
    textval = ''
    if length:
        length += 1
        buffer_ = (ctypes.c_wchar * length)()
        ret =  windll.user32.GetWindowTextW(
            handle, ctypes.byref(buffer_), length)
        if ret:
            textval = buffer_.value
    return textval

def activate_pidgin():
    windows = [(h, classname(h), text(h)) for h in enum_windows()]
    pidgin = [w for w in windows if 'gdkWindowToplevel' == w[1] \
                and "Buddy List" != w[2]]
    
    for w in pidgin:
        if w[2].startswith(("#", "NickServ", "ChanServ", "freenode")):
            windll.user32.SetForegroundWindow(w[0])
            break