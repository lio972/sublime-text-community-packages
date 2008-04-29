import ctypes, re, SendKeys
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
            
def findAppHandle(classMatch='', textMatch='', textNot=''):
    classRX, textRX, textNot = map(re.compile, [classMatch, textMatch,textNot])
    
    windows = [(h, classname(h), text(h)) for h in enum_windows()]
    app = [w for w in windows if classRX.search(w[1]) \
                             and textRX.search(w[2])  \
                         and not textNot.search(w[2]) ]
                         
    return app[0][0] if app else 0# len(app) == 1 else 0
        

def activateApp( windowClassMatch='', 
                 windowTitleTextMatch='',
                 windowTitleTextNot='', 
                 sendKeysOnlyIfTextMatch='', 
                 sendKeys=''):
                    
    h = findAppHandle(windowClassMatch, windowTitleTextMatch, windowTitleTextNot)
    if h:
        windll.user32.SetForegroundWindow(h)
        if sendKeys:
            alwaysSend = sendKeysOnlyIfTextMatch is ''
            if re.search(sendKeysOnlyIfTextMatch, text(h)) or alwaysSend:
                SendKeys.SendKeys(sendKeys)
    return h