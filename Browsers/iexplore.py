################################## IMPORTS #####################################

import time, threading, Queue, functools

from ctypes import windll
from comtypes.client import CreateObject
from windows import SetForegroundWindow

################################################################################

DEBUG = 1

################################################################################

def command(func):
    @functools.wraps(func)
    def put(self, *args):  
        self.Q.put((func, args))
    return put

class ThreadedIE(threading.Thread):
    def __init__ (self):
        threading.Thread.__init__ (self)
        self.Q = Queue.Queue()
        self.start()
    
    @command
    def toggleVisible(ie):
        ie.Visible = not ie.Visible
    
    @command
    def navigate(ie, url):
        ie.Navigate(url)
        while ie.ReadyState != 4: pass
    
    @command
    def write(ie, buf):
        if ie.ReadyState != 4: pass

        ie.Document.open()
        ie.Document.write(buf)
        ie.Document.close()

    @command
    def refresh(ie):
        ie.Refresh()

    @command
    def buffer(ie, buf):
        try: ie.Document.body.innerHTML = buf
        except: return
        while ie.ReadyState != 4:  pass

    def run (self):
        windll.ole32.CoInitializeEx(None, 0x2)

        ie = CreateObject('InternetExplorer.Application')

        ie.ToolBar = 0
        ie.StatusBar = 0
        ie.Visible = 1

        while True:
            ie_command, args = self.Q.get()
            try:      ie_command(ie, *args)
            except:   break
            finally:  self.Q.task_done()

        windll.ole32.CoUninitialize()

################################################################################

def IE():
    ie = CreateObject("InternetExplorer.Application")
    ie.__class__.activate = lambda s: SetForegroundWindow(s.HWND)
    return ie

################################################################################