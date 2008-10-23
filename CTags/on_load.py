################################################################################

from __future__ import with_statement
import sublimeplugin

if not hasattr(sublimeplugin.onActivated, '__wrapped__'):
    import sublime
    import functools
    import threading
    
    from os.path import normpath
    
    def onActivated(f):        
        @functools.wraps(sublimeplugin.onActivated)
        def wrapper(v):
            w = v.window()
            if w:
                sublime._activeWindow = w
            
            if not v.isLoading():
                fn = normpath(v.fileName() or '')
                while sublime.on_load_cbs.get(fn):
                    sublime.on_load_cbs[fn].pop()(v)

            f(v)
        
        return wrapper
    
    sublime.on_load_cbs = {}
    sublime.cb_lock     = threading.RLock()
    
    def addOnLoadCallback(f, cb):
        with sublime.cb_lock:
            sublime.on_load_cbs.setdefault(normpath(f), []).append(cb)
    
    def activeWindow():
        return sublime._activeWindow
    
    sublime.activeWindow = activeWindow
    sublime.addOnLoadCallback = addOnLoadCallback
    sublimeplugin.onActivated.__wrapped__ = 1
    sublimeplugin.onActivated = onActivated(sublimeplugin.onActivated)
    
################################################################################