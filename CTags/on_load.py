################################################################################

from __future__ import with_statement
from ctypes import windll
import sublimeplugin

if not hasattr(sublimeplugin.onLoad, '__wrapped__'):
    import sublime
    import functools
    import threading
    
    from os.path import normpath
    

    def onActivated(f):
        @functools.wraps(sublimeplugin.onActivated)
        def wrapper(v):
            w = v.window()
            if w:
                # _windows['all'][w.id()] = w
                _windows['latest'] = w
                # _windows['hwnd'][w.id()] = windll.user32.GetForegroundWindow()

            f(v)

        return wrapper


    def onLoad(f):        
        @functools.wraps(sublimeplugin.onLoad)
        def wrapper(v):            
            for cb in reversed(on_load_cbs.get(v.bufferId(), [])):
                cb(v)

            f(v)

        return wrapper
    
    on_load_cbs = {}
    cb_lock     = threading.RLock()
    _windows    = {'all': {}, 'latest': None, 'hwnd': {}}
    
    def addOnLoadedCallback(view, cb):
        with cb_lock:
            on_load_cbs.setdefault(view.bufferId(), []).append(cb)

    def activeWindow():
        return _windows.get('latest')
        
    # def windows():
    #     return sorted(_windows['all'].values(), key=lambda w: w.id())

    # def hwnd(w):
    #     return _windows['hwnd'][w.id()]

    sublime.activeWindow = activeWindow
    # sublime.windows = windows
    # sublime.Window.hwnd = hwnd

    sublime.addOnLoadedCallback = addOnLoadedCallback
    sublimeplugin.onLoad = onLoad(sublimeplugin.onLoad)
    sublimeplugin.onActivated = onActivated(sublimeplugin.onActivated)
    
    sublimeplugin.onLoad.__wrapped__ = 1

################################################################################