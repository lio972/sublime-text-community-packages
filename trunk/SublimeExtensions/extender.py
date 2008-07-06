################################################################################

import sublime, sublimeplugin

import time, functools, threading

from ctypes import windll

################################################################################
# Views maintainer
# 

sublime.allViews = {}

class ViewsMaintainer(sublimeplugin.Plugin):
    """
    
    MAPPING = {
        "keymaps" : lambda v: v.fileName().endswith('keymap'),
        "python"    : lambda v: 'ython' in v.options().get('syntax')
    }
    
    class CloseFilesCommand(sublimeplugin.TextCommand):
        def run(self, view, args):
            matchesCriteria = MAPPING[args[0]]
    
            fn = view.fileName()
            w = view.window()
         
            for f, v in sublime.allViews.items():
                if matchesCriteria(v):           # matches criteria
                    w.openFile(f)                # activate that file
                    w.runCommand('close')        # close it
    
            # activate file originally open
            if fn and not matchesCriteria(view): 
                w.openFile(fn)
    
    """
    def onLoad(self, view):
        fn = view.fileName()
        if fn:
            sublime.allViews[fn] = view

    def onClose(self, view):
        fn = view.fileName()
        if fn and fn in sublime.allViews:
            del sublime.allViews[fn]

    onClone = onNew = onActivated = onLoad

################################################################################
# Get whole buffer
"""
>>> view.buffer
import sublime .....

"""
sublime.View.buffer = property(lambda v: v.substr(sublime.Region(0, v.size())))

################################################################################
# Get and set Options

# TODO: look at monkey patching Options.(__setattr__ | __getattr__)

"""

>>> view.option.syntax 
u'Packages/Python/Python.tmLanguage'

"""

OPTIONS = (
    'syntax',   
)

sublime.View.option = property(lambda v: v.options())

for option in OPTIONS:
    setattr(sublime.Options, option,
        property ( lambda o: o.get(option), lambda o, v: o.set(option, v))
    )

################################################################################
# Idle timeout decorators
#
def onIdle(ms=1000):
    """
    
    http://www.sublimetext.com/docs/plugin-examples
    
     1. class IdleWatcher(sublimeplugin.Plugin):  
     2.     pending = 0  
     3.       
     4.     def handleTimeout(self, view):  
     5.         self.pending = self.pending - 1  
     6.         if self.pending == 0:  
     7.             # There are no more queued up calls to handleTimeout, so it must have  
     8.             # been 1000ms since the last modification  
     9.             self.onIdle(view)  
    10.   
    11.     def onModified(self, view):  
    12.         self.pending = self.pending + 1  
    13.         # Ask for handleTimeout to be called in 1000ms  
    14.         sublime.setTimeout(functools.partial(self.handleTimeout, view), 1000)  
    15.   
    16.     def onIdle(self, view):  
    17.         print "No activity in the past 1000ms"  
    
    
        
    decorator for IdleWatcher pattern:
        Wraps a function so that it is only called when not called for ms 
        milliseconds.
    
    class IdleWatcher(sublimeplugin.TextCommand):
        def onModified(self, view):
            # do other stuff
            self.onIdle(1,2,3, somekey = 'arst')
        
        @sublimeplugin.onIdle(ms=1000)
        def onIdle(self, a1, a2, a3, somekey=None):
            print a1, a2, a3, somekey

    """
    def decorator(func):
        func.pending = 0
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            def idle():
                func.pending -= 1
                if func.pending is 0:
                    func(*args, **kwargs)
            func.pending +=1
            sublime.setTimeout(idle, ms)
        return wrapped
    return decorator

sublimeplugin.onIdle = onIdle

################################################################################
# threaded, 1 at a time decorator
#
def threaded(finish=None, msg="Thread already running"):
    """
    
    Wraps a function call in a thread, and only allows one thread to run at a 
    time.
    
    finish is the function to call in main thread with results of the @threaded 
    function.

    msg will be displayed in status bar if thread already running

    eg.

    class ThreadedCommand(sublimeplugin.TextCommand):
        def run(self, view, args):
            self.printout()
        
        def finitre(self, result):
            print result
    
        @sublimeplugin.threaded(finitre)
        def printout(self):
            time.sleep(5)
            return 'hey from thread'

    """
    def decorator(func):
        func.running = 0
        @functools.wraps(func)
        def threaded(*args, **kwargs):
            def run():
                result = func(*args, **kwargs)
                if finish:
                    sublime.setTimeout (
                        functools.partial(finish, args[0], result), 0
                    )
                func.running = 0
            if not func.running:
                func.running = 1
                threading.Thread(target=run).start()
            else:
                sublime.statusMessage(msg)
        return threaded
    return decorator

sublimeplugin.threaded = threaded

################################################################################

class FocusRestorer(object):
    def __init__(self): 
        self.h = windll.user32.GetForegroundWindow()
    def __call__(self, times=2, delay = 50):  
        for t in xrange(1, (delay * times) + 2, delay):
            sublime.setTimeout (
                functools.partial(windll.user32.SetForegroundWindow, self.h), t
            )

sublime.FocusRestorer = FocusRestorer

################################################################################