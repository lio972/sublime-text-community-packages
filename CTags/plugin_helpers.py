import functools
import sublime
import threading
import time

from ctypes import windll, create_unicode_buffer

def threaded(finish=None, msg="Thread already running"):
    def decorator(func):
        func.running = 0
        @functools.wraps(func)
        def threaded(*args, **kwargs):
            def run():
                try:
                    result = func(*args, **kwargs)
                    if finish:
                        sublime.setTimeout (
                            functools.partial(finish, args[0], result), 0
                        )
                finally:
                    func.running = 0
            if not func.running:
                func.running = 1
                threading.Thread(target=run).start()
            else:
                sublime.statusMessage(msg)
        return threaded
    return decorator

class FocusRestorer(object):
    def __init__(self):
        self.h = windll.user32.GetForegroundWindow()
    def __call__(self, times=2, delay = 50):  
        for t in xrange(1, (delay * times) + 2, delay):
            sublime.setTimeout (
                functools.partial(windll.user32.SetForegroundWindow, self.h), t
            )

def in_main(f):
    @functools.wraps(f)
    def done_in_main(*args, **kw):
        sublime.setTimeout(functools.partial(f, *args, **kw), 0)
        
    return done_in_main