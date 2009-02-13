################################################################################
from __future__ import with_statement

# Std Libs
import traceback
import threading
import sys
import functools
import tempfile
import os

from ctypes import windll

setwh = windll.user32.SetForegroundWindow
getwh = windll.user32.GetForegroundWindow

from os.path import normpath, splitext, splitdrive, join, dirname, exists

# Sublime Modules
import sublime
import sublimeplugin

# 3rd Party Libs
import Pyro.core

################################################################################

def eval_in_main(f):
    event = threading.Event()
    f._exception = None
   
    def in_main():
        try:
            f._result = f()
        except Exception, e:
            f._exception = traceback.format_exc(e)
        finally:
            event.set()

    sublime.setTimeout(in_main, 0)
    event.wait()

    if f._exception:    raise Exception(f._exception)
    else:               return f._result

################################################################################

tempFiles = {}

sbwh = None

class RemoteEditHelperPlugin(sublimeplugin.TextCommand):
    def run(self, view, args):
        self.onClose(view)

    def onClose(self, view):
        global sbwh 
        sbwh = getwh()
        
        fn = normpath(view.fileName() or '')
        if fn in tempFiles:
            tempFiles[fn].set()

################################################################################

class Sublime(Pyro.core.ObjBase):
    def editBuffer(self, text, fn=None):
        wh = getwh()
        if sbwh: setwh(sbwh)
        
        if fn:
            fn = splitdrive(normpath(fn))[1].lstrip('\\/')
            
            temp_file = join("D:\\remote_sublime_edit", fn)
            try:  os.makedirs(dirname(temp_file))
            except Exception, e:  pass

        temp_file = normpath(temp_file)
        
        with open(temp_file, 'w') as fh: fh.write(text)
        
        @eval_in_main
        def open_temp_file():
            tempFiles[temp_file] = threading.Event()
            sublime.activeWindow().openFile(temp_file)

        tempFiles[temp_file].wait()

        sublime.setTimeout(functools.partial(setwh, wh), 0)

        with open(temp_file) as fh: return fh.read()

    def testServer(self):
        return "OK"

################################################################################

if 1:
    Pyro.core.initServer()
    daemon=Pyro.core.Daemon(port=11521, norange=True)
    uri=daemon.connect(Sublime(), "sublime")
    
    print "The daemon runs on port:",daemon.port
    print "The object's uri is:",uri
    
    server_thread = threading.Thread(target=daemon.requestLoop)
    server_thread.setName('PYRO Server')
    server_thread.start()

################################################################################