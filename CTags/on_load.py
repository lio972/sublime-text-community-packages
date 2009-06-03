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
                while on_load_cbs.get(fn):
                    on_load_cbs[fn].pop()(v)

            f(v)

        return wrapper
    
    on_load_cbs = {}
    cb_lock     = threading.RLock()
    
    def addOnLoadedCallback(f, cb):
        with cb_lock:
            on_load_cbs.setdefault(normpath(f), []).append(cb)

    def activeWindow():
        return sublime._activeWindow

    sublime.activeWindow = activeWindow
    sublime.addOnLoadedCallback = addOnLoadedCallback
    sublimeplugin.onActivated = onActivated(sublimeplugin.onActivated)
    sublimeplugin.onActivated.__wrapped__ = 1

################################################################################