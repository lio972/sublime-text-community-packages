import ctypes, re, os
from ctypes import *
from functools import partial

GetForegroundWindow = windll.user32.GetForegroundWindow
SetForegroundWindow = windll.user32.SetForegroundWindow

OFN_ALLOWMULTISELECT =  512
OFN_CREATEPROMPT =  8192
OFN_DONTADDTORECENT =  33554432
OFN_ENABLEHOOK =  32
OFN_ENABLEINCLUDENOTIFY =  4194304
OFN_ENABLESIZING =  8388608
OFN_ENABLETEMPLATE =  64
OFN_ENABLETEMPLATEHANDLE =  128
OFN_EXPLORER =  524288
OFN_EXTENSIONDIFFERENT =  1024
OFN_EX_NOPLACESBAR =  1
OFN_FILEMUSTEXIST =  4096
OFN_FORCESHOWHIDDEN =  268435456

OFN_HIDEREADONLY =  4

OFN_LONGNAMES =  2097152
OFN_NOCHANGEDIR =  8

OFN_NODEREFERENCELINKS =  1048576

OFN_NOLONGNAMES =  262144
OFN_NONETWORKBUTTON =  131072
OFN_NOREADONLYRETURN =  32768
OFN_NOTESTFILECREATE =  65536
OFN_NOVALIDATE =  256
OFN_OVERWRITEPROMPT =  2
OFN_PATHMUSTEXIST =  2048
OFN_READONLY =  1
OFN_SHAREAWARE =  16384
OFN_SHAREFALLTHROUGH =  2
OFN_SHARENOWARN =  1
OFN_SHAREWARN =  0
OFN_SHOWHELP =  16

#http://msdn2.microsoft.com/en-us/library/ms646839(VS.85).aspx
class OPENFILENAME(ctypes.Structure):
    _fields_ = (("lStructSize", c_int),
        ("hwndOwner", c_int),
        ("hInstance", c_int),
        ("lpstrFilter", c_wchar_p),
        ("lpstrCustomFilter", c_char_p),
        ("nMaxCustFilter", c_int),
        ("nFilterIndex", c_int),
        ("lpstrFile", c_wchar_p),
        ("nMaxFile", c_int),
        ("lpstrFileTitle", c_wchar_p),
        ("nMaxFileTitle", c_int),
        ("lpstrInitialDir", c_wchar_p),
        ("lpstrTitle", c_wchar_p),
        ("flags", c_int),
        ("nFileOffset", c_ushort),
        ("nFileExtension", c_ushort),
        ("lpstrDefExt", c_char_p),
        ("lCustData", c_int),
        ("lpfnHook", c_char_p),
        ("lpTemplateName", c_char_p),
        ("pvReserved", c_char_p),
        ("dwReserved", c_int),
        ("flagsEx", c_int))

    def __init__(self, title):
        ctypes.Structure.__init__(self)
        self.lStructSize = ctypes.sizeof(OPENFILENAME)
        self.nMaxFile = 1024
        # self.hwndOwner = win
        self.lpstrTitle = title
        # self.Flags = OFN_EXPLORER | OFN_ALLOWMULTISELECT | OFN_NODEREFERENCELINKS

def openFileDialog(title="Open File", flags= OFN_EXPLORER | OFN_ALLOWMULTISELECT):
    ofx = OPENFILENAME(title)
    
    opath = u"\0" * 1024
    ofx.lpstrFile = opath
    ofx.flags = flags
        
    # filters = sorted(self.OptionsFromSuffix(".filter").values())
    # filterText = unicode("\0".join([f.replace("|", "\0") for f in filters])+"\0\0")
    # ofx.lpstrFilter = filterText

    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofx)):
        paths = opath.strip('\0').split("\0")
        
        if len(paths) > 1:
            return [os.path.join(paths[0], x) for x in paths[1:]]
        else:
            return paths

        # opath.replace(u"\0", u"")
        # self.GrabFile(absPath)
        # self.FocusText()
        
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

def findAppHandle(classMatch='', textMatch=''):
    classRX, textRX = map(re.compile, [classMatch, textMatch])
    
    windows = [(h, classname(h), text(h)) for h in enum_windows()]
    app = [w for w in windows if classRX.match(w[1]) and textRX.match(w[2])]
    return app[0][0] if app else 0# len(app) == 1 else 0
        
def activateApp(classMatch='', textMatch=''):
    h = findAppHandle(classMatch, textMatch)
    if h: windll.user32.SetForegroundWindow(h)
    return h