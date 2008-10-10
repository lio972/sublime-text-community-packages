################################################################################

# Std Libs
from __future__ import with_statement

import SimpleXMLRPCServer
import threading
import functools
import tempfile
import time
import os

# Sublime Libs
import sublime
import sublimeplugin

################################################################################

def normpath(p):
    return os.path.normpath(p or '').lower()

def in_main(f):
    @functools.wraps(f)
    def done_in_main(*args, **kw):
        sublime.setTimeout(functools.partial(f, *args, **kw), 0)

    return done_in_main

################################################################################

sublime.tempFiles = {}

@in_main
def open_tempf(tempf):
    # can store meta l8r eg onClose vs onSave
    sublime.tempFiles[tempf] = True

    sublime.activeWindow.openFile(tempf)
    # TODO: SetForegroundWindow(sublime.wndh)

def block_while_editing_tempf(tempf, opening=False):
    if opening: 
        while tempf not in sublime.tempFiles: time.sleep(0.01)
    
    while tempf in sublime.tempFiles:    time.sleep(0.01)

################################################################################

class RemoteEditHelperPlugin(sublimeplugin.Plugin):
    def onActivated(self, view):
        sublime.activeWindow = view.window()
        
    def onClose(self, view):
        fn = normpath(view.fileName())
        if fn in sublime.tempFiles:
            sublime.tempFiles.pop(fn)

################################################################################

class SublimeText(object):
    def editBuffer(self, text, file_name=None):
        tempf = normpath(tempfile.mktemp())
        
        # TODO: encodings ??

        with open(tempf, 'w') as fh:    fh.write(text)

        open_tempf(tempf)
        block_while_editing_tempf(tempf, opening=1)
        
        with open(tempf) as fh:         return fh.read()
    
    def testServer(self):
        return 'OK'

################################################################################

class RPCServer(object):
    def __init__(self):
        self.t = threading.Thread(target = self.startServer)
        self.t.start()

    def startServer(self):
        self.sublime = SublimeText()

        self.server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", 8000))
        self.server.register_instance(self.sublime)
        self.server.serve_forever()

command_server = RPCServer()

################################################################################