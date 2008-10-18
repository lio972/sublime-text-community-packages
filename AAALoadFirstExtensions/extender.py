# coding: utf8
################################################################################

import time
import functools
import threading
import os
import sys

from ctypes import windll, create_unicode_buffer

import sublime
import sublimeplugin

################################################################################
# Get whole buffer
"""
>>> view.buffer
import sublime .....

"""
sublime.View.buffer = property(lambda v: v.substr(sublime.Region(0, v.size())))

################################################################################
# Get and set Options

"""

>>> view.option.syntax 
u'Packages/Python/Python.tmLanguage'

"""

class SublimeOptions(object):
    def __setattr__(self, name, value):
        self.options.set(name, value)
    def __getattr__(self, name):
        if hasattr(self.options, name):
            return getattr(self.options, name)
        return self.options.get(name)
    def __init__(self, view):
        self.__dict__['options'] = view.options()

sublime.View.option = property(lambda v: SublimeOptions(v))

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

############################   UNICODE SYS.PATH   ##############################

def addSublimePackage2SysPath(packageName='', module=''):
    """                    
    
    usage:
        
        # coding: utf8      

        # You must declare encoding on first or second line if using unicode
        

        addSublimePackage2SysPath( unicode('山科 氷魚', 'utf8') )
        
            or
        
        addSublimePackage2SysPath(u'RegexBuddy')
                
            or
            
        addSublimePackage2SysPath(packageName='Package', module='zipimport.egg')
    
    """
    
    unicodeFileName = os.path.join (
        
        sublime.packagesPath(), packageName, 'Lib', module
        
    ).rstrip('\\')
        
    buf = create_unicode_buffer(512)
    if not windll.kernel32.GetShortPathNameW( unicodeFileName, buf, len(buf)):

        sublime.messageBox (

          'There was an error getting 8.3 shortfile names for %s package. ' 
          'These are relied upon as python does not support unicode for its '
          'module paths. Make sure shortpath names are ENABLED and take steps '
          'to make sure they have been created before trying again.'        %\
                packageName
        )
        
        import webbrowser
        try: webbrowser.open('http://support.microsoft.com/kb/210638')
        except: pass
        
        raise Exception('Error with GetShortPathNameW')
    
    path = buf.value.encode('ascii')
    if path not in sys.path:
        sys.path.insert(1, path)

sublimeplugin.addSublimePackage2SysPath = addSublimePackage2SysPath

################################################################################

class SublimeCommands(object):
    def runCommands(self, *args, **kwargs):
        for t in xrange(kwargs.get('times', 1)):
            self.obj.runCommand(self.command, self.args + list(args))
        return self

    def __getattr__(self, name):
        args = name.split("_")
        self.args = args[1:]
        self.command = args[0]
        return self.runCommands
    
    def __init__(self, obj): 
        self.obj = obj

sublime.View.cmd = property(lambda s: SublimeCommands(s))
sublime.Window.cmd = property(lambda s: SublimeCommands(s))

################################################################################

sublime.View.cb = property( lambda s: sublime.getClipboard(), 
                            lambda s, o: sublime.setClipboard(o))

################################################################################