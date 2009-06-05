################################################################################
# Std Libs

from __future__ import with_statement

import functools
import sys
import string
import textwrap

from itertools import takewhile
from os.path import join

# 3rd Party Libs
import Pyro.core

# Sublime Modules
import sublime
import sublimeplugin

# User Libs

from pywinauto_ipython import launch_ipython
from windows import activateApp
completion_server = join(sublime.packagesPath(), 'IPython', 'server')

################################################################################

def consume(iterable, i=None):
    'Returns the last in an iterable or defaults to i if None in iterable'
    for i in iterable: pass
    return i

def contig(view, pt):
    if isinstance(pt, sublime.Region): pt = pt.begin()
    notAtBoundary = lambda p: view.substr(p) not in string.whitespace

    start = consume(takewhile(notAtBoundary, xrange(pt-1, -1, -1)),      pt)
    end   = consume(takewhile(notAtBoundary, xrange(pt, view.size())), pt-1)

    return sublime.Region(start, end + 1)

################################################################################

class IPythonBridge(sublimeplugin.TextCommand):
    pywinauto_ip   = None

    def __init__(self):
        self.reset()
        self.installAutoCompletion()

    def reset(self):
        self.connected = False
        self.IP = Pyro.core.getProxyForURI("PYROLOC://localhost:7380/IPython")
        self.history_length = 0
        self.history_pos    = -1

    def statusMessage(self, msg):
        sublime.statusMessage("%s: %s" % (self.__class__.__name__, msg))

    def installAutoCompletion(self):
        from AutoComplete import AutoCompleteCommand
        AutoCompleteCommand.completionCallbacks['ipython'] = self.auto_completion

    def launchIPython(self, view):
        # TODO attach to ipython
        if not self.pywinauto_ip:
            self.pywinauto_ip = launch_ipython(completion_server)
        else:
            try:
                self.pywinauto_ip.TypeKeys('', 0)
            except Exception:
                try:
                    self.pywinauto_ip = launch_ipython(completion_server)
                except Exception, e:
                    self.pywinauto_ip = None

    def historyLines(self, view, direction):
        history = self.IP.input_hist()
        history_length = len(history)

        if history_length != self.history_length:
            self.history_length = history_length
            self.history_pos = -1
        else:
            if direction == 'up':     self.history_pos -= 1
            else:                     self.history_pos += 1

        index = (self.history_pos % (history_length-1)) + 1
        history_line = history[index]

        indexed_line = 'In[%s] %s' % (index, history_line)
        sel = view.sel()[0]
        sublime.statusMessage(indexed_line)

        view.replace(sel, history_line)
    
    def importHistory(self, view):
        history = ''.join(sorted(self.IP.import_hist(), reverse=True))
        view.runCommand('insertInlineSnippet', ['$PARAM1', history])
        
    
    def pushLines(self, view):
        lines = []
        for sel in view.sel():
            for l in view.substr(view.fullLine(sel)).splitlines(1):
                lines += [l]
        to_push = textwrap.dedent(''.join(lines))
        self.IP.push(to_push)
        self.statusMessage('%s lines pushed to IPython' % len(lines))

    def auto_completion(self, view, pos, prefix, completions):
        if view.matchSelector(0, 'source.python') and self.connected:
            contiguous_region = contig(view, pos)
            contiguous = view.substr(contiguous_region)
            current_line = view.substr(view.line(view.sel()[0])).lstrip()
            
            completion, matches = self.IP.complete(contiguous, current_line)
            prefix_length_diff = len(contiguous) - len(prefix)
            
            if prefix_length_diff < 0:
                operation = lambda s: ' ' + s
            else:
                operation = lambda s: s[prefix_length_diff:]
            
            matches = sorted( (operation(s) for s in matches), 
                              reverse=True )

            for c in (m for m in matches if m not in completions):
                completions.append(c)

        return completions

    def run(self, view, args):
        try:
            getattr(self, args[0])(view, *args[1:])
            self.connected = True
        except Exception, e:
            self.statusMessage(e)
            self.reset()

            if e.message == 'connection failed':
                view.runCommand('iPythonBridge')

class InsertIPythonCompletion(sublimeplugin.TextCommand):
    def run(self, view, args):
        v = sublime.activeWindow().activeView()
        v.replace(contig(v, v.sel()[0].end()), args[0])

################################################################################