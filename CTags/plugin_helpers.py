#################################### IMPORTS ###################################

import sublime

import functools
import threading
import time
from os.path import normpath
from ctypes import windll

################################################################################

def staggered(every=1):
    def co_routine(f):
        @functools.wraps(f)
        def run(*args):
            routine = f(*args)
    
            def next():
                try:                   routine.next()
                except StopIteration:  return
                sublime.setTimeout(next, every)
        
            next()
        return run
    return co_routine

################################################################################

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

################################################################################

class FocusRestorer(object):
    def __init__(self):
        self.h = windll.user32.GetForegroundWindow()
    def __call__(self, times=2, delay = 50):  
        for t in xrange(1, (delay * times) + 2, delay):
            sublime.setTimeout (
                functools.partial(windll.user32.SetForegroundWindow, self.h), t
            )

################################################################################

def in_main(f):
    @functools.wraps(f)
    def done_in_main(*args, **kw):
        sublime.setTimeout(functools.partial(f, *args, **kw), 0)
        
    return done_in_main

################################################################################


def view_fn(view, if_None = '.'):
    return normpath(view.fileName() or if_None)

def quick_panel(display, on_select, on_cancel=None, flags=0, *args, **kw):
    sublime.activeWindow().showSelectPanel (
        display, on_select, on_cancel, flags, *args, **kw)

def wait_until_loaded(file):
    def wrapper(f):
        sublime.addOnLoadedCallback(file, f)
        sublime.activeWindow().openFile(file)

    return wrapper

def select(view, region):
    sel_set = view.sel()
    sel_set.clear()
    sel_set.add(region)
    view.show(region)

################################################################################