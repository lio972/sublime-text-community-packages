################################################################################

import time
import functools
import threading
import os
import sys

from ctypes import windll, create_unicode_buffer
from os.path import normpath, join, dirname, split, splitext, isabs

import sublime
import sublimeplugin

################################################################################
# threaded, 1 at a time decorator
#
def threaded(finish=None, msg="Thread already running"):
    """

    Wraps a function call in a thread, and only allows one thread to run at a 
    time.

    ``finish`` is the function to call in main thread with ``result`` of the
    threaded decorated function.

        if not isinstance(result, tuple):
            result = (result, )

        finish(self, *result)

    ``msg`` will be displayed in the status bar if thread already running

    eg.

    class ThreadedCommand(sublimeplugin.TextCommand):
        def run(self, view, args):
            self.printout()
        
        def finitre(self, result):
            print result
        
        def some_other_command():
            if self.printout.running:
                do_stuff()

        @threaded(finitre)
        def printout(self):
            time.sleep(5)
            return 'hey from thread'

    """

    def decorator(func):
        func.running = 0
        @functools.wraps(func)
        def threaded(*args, **kwargs):
            def run():
                try:
                    result = func(*args, **kwargs)
                    if not isinstance(result, tuple):
                        result = (result, )
                    if finish:
                        sublime.setTimeout (
                            functools.partial(finish, args[0], *result), 0
                        )
                finally:
                    func.running = 0
            if not func.running:
                func.running = 1
                threading.Thread(target=run).start()
            else:
                if callable(msg): msg = msg()
                sublime.statusMessage(msg)
        return threaded
    return decorator

def view_fn(view, if_None = '.'):
    return normpath(view.fileName() or if_None)

def wait_until_loaded(file):
    def wrapper(f):
        sublime.addOnLoadedCallback(file, f)
        sublime.activeWindow().openFile(file)

    return wrapper