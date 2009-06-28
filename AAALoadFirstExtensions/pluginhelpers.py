#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
from __future__ import with_statement

import time
import functools
import threading
import os
import sys
import re
import types

from os.path import normpath, join
from ctypes import windll, create_unicode_buffer

# Sublime
import sublime
import sublimeplugin

from sublimeconstants import RE_SPECIAL_CHARS

#################################### HELPERS ###################################

def escapeRegex(s):
    return RE_SPECIAL_CHARS.sub(lambda m: '\\%s' % m.group(1), s)
escape_regex = escapeRegex

def viewFn(view, ifNone = ''):
    "Should be a monkey patch for ifNone default"
    return normpath(view.fileName() or ifNone)
view_fn = viewFn

def doIn(t=0):
    def timeout(f):
        return sublime.setTimeout(f, t)
    return timeout
do_in = doIn

def wait_until_loaded(file):
    def wrapper(cb):
        view = sublime.activeWindow().openFile(file)
        if view.isLoading():
            sublime.addOnLoadedCallback(view, cb)
        else:
            cb(view)

    return wrapper
waitUntilLoaded = wait_until_loaded

def asset_path(f):
    pkg_path = sublime.packagesPath()
    return join('Packages', f[len(pkg_path)+1:]).replace("\\", '/')

def select(view, region):
    selSet = view.sel()
    selSet.clear()
    selSet.add(region)
    view.show(region)

################################## DECORATORS ##################################

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
on_idle = onIdle

def staggered(every=1):
    def generator(f):
        @functools.wraps(f)
        def run(*args):
            routines = [f(*args)]

            def next():
                try:
                    ret = routines[-1].next()

                except StopIteration:
                    del routines[-1]

                    if not routines:
                        return
                    else:
                        next()
                else:
                    if isinstance(ret, types.GeneratorType ):
                        routines.append(ret)

                    sublime.setTimeout (
                        next,
                        ret if isinstance(ret, int) else every )

            next()
        return run
    return generator

def threaded(finish=None, msg="Thread already running"):
    """
    
    Wraps a function call in a thread, and only allows one thread to run at a 
    time.
    
    ``finish`` is the function to call in main thread with results of the
    decorated function

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
    
    If some other function requires to know if thread is still running
    then check `running` attribute of the function in question.

    eg.

        if not self.printout.running:
            doStuff()
        else:
            sublime.messageBox('Hold your horses buddy!')
    

    """
    def decorator(func):
        func.running = 0
        @functools.wraps(func)
        def threaded(*args, **kwargs):
            def run():
                try:
                    result = func(*args, **kwargs)
                    if result is None:
                        result = ()

                    elif not isinstance(result, tuple):
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
                sublime.statusMessage(msg)
        threaded.func = func
        return threaded
    return decorator

################################################################################

def in_main(f):
    @functools.wraps(f)
    def done_in_main(*args, **kw):
        sublime.setTimeout(functools.partial(f, *args, **kw), 0)

    return done_in_main

def quick_panel(display, on_select, on_cancel=None, flags=0, *args, **kw):
    sublime.activeWindow().showSelectPanel (
        display, on_select, on_cancel, flags, *args, **kw)

############################### RESTORE APP FOCUS ##############################

class FocusRestorer(object):
    def __init__(self):
        self.h = windll.user32.GetForegroundWindow()
    def __call__(self, times=2, delay = 50):
        for t in xrange(1, (delay * times) + 2, delay):
            sublime.setTimeout (
                functools.partial(windll.user32.SetForegroundWindow, self.h), t
            )

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

        sublime.packagesPath(), packageName, module

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

################ activeWindow addOnLoadedCallback monkeypatches ################

if not hasattr(sublimeplugin.onLoad, '__wrapped__'):
    def onActivated(f):
        @functools.wraps(sublimeplugin.onActivated)
        def wrapper(v):
            w = v.window()
            if w:
                sublime._activeWindow = w

            cbs = on_activated_cbs.pop(v.bufferId(), [])
            while cbs: cbs.pop()(v)

            f(v)

        return wrapper

    def onLoad(f):
        @functools.wraps(sublimeplugin.onLoad)
        def wrapper(v):
            w = v.window()

            cbs = on_load_cbs.pop(v.bufferId(), [])
            defer =  len(on_load_cbs)

            while cbs:
                cb = cbs.pop()

                if defer:    addOnActivatedCallback(v, cb)
                else:        cb(v)

            f(v)

        return wrapper

    on_load_cbs = {}
    on_activated_cbs = {}

    cb_lock     = threading.RLock()

    def addOnLoadedCallback(view, cb):
        with cb_lock:
            on_load_cbs.setdefault(view.bufferId(), []).append(cb)

    def addOnActivatedCallback(view, cb):
        with cb_lock:
            on_activated_cbs.setdefault(view.bufferId(), []).append(cb)

    def activeWindow():
        return sublime._activeWindow

    sublime.activeWindow = activeWindow
    sublime.addOnLoadedCallback = addOnLoadedCallback

    sublimeplugin.onLoad = onLoad(sublimeplugin.onLoad)
    sublimeplugin.onActivated = onActivated(sublimeplugin.onActivated)

    sublimeplugin.onLoad.__wrapped__ = 1

################################# CONVENIENCES #################################

class SublimeOptions(object):
    """
    
    >>> view.option.syntax 
    u'Packages/Python/Python.tmLanguage'
    
    """

    def __setattr__(self, name, value):
        self.options.set(name, value)
    def __getattr__(self, name):
        if hasattr(self.options, name):
            return getattr(self.options, name)
        return self.options.get(name)
    def __init__(self, view):
        self.__dict__['options'] = view.options()

class SublimeMacro(object):
    def runCommands(self, *args, **kwargs):
        cmd = sublime.makeCommand(self.command, self.args + list(args))

        for t in xrange(kwargs.get('times', 1)):
            self._obj.runCommand(cmd)
            self._cmds.append(cmd)

        return self

    def __getattr__(self, name):
        args = name.split("_")
        self.args = args[1:]
        self.command = args[0]
        return self.runCommands

    def __repr__(self):
        return '\n#Macro:\n%s\n' % '\n'.join(self._cmds)

    def __init__(self, _obj):
        self._cmds = []
        self._obj = _obj

################################ MONKEY-PATCHES ################################

def patches(cls, wrapper=None):
    def patcher(f):
        setattr(cls, f.__name__, wrapper(f) if wrapper else f)
        return f
    return patcher

################################################################################