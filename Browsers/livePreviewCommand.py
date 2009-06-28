# coding: utf8

################################## IMPORTS #####################################

from __future__ import with_statement

import gc

import sublime, sublimeplugin, re,  functools

import iexplore, processors

################################## SETTINGS ####################################

DEBUG = iexplore.DEBUG = processors.DEBUG = 1

TIMEOUT = 35

################################## CONSTANTS ###################################

reFlags = re.DOTALL | re.IGNORECASE | re.MULTILINE
headRe = re.compile("(<head.*?>.*?</head>)", reFlags)

################################################################################

def whenActive(func):
    @functools.wraps(func)
    def isActive(self, view):
        if self.isActive() and self.visible:
            func(self, view)
    return isActive

################################################################################

class LivePreviewCommand(sublimeplugin.TextCommand):
    procQ = None

    def __init__(self):
        self.reset()

    def run(self, view, args):
        if not self.ie:
            self.init(view)
        else:
            if self.isActive():
                self.visible = not self.visible
                self.ie.toggleVisible()
                self.restoreFocus()
            else:
                self.run(view, args)

    def readyIE(self):
        self.ie = iexplore.ThreadedIE()
        self.visible = True
        self.restoreFocus()

    def init(self, view):
        self.restoreFocus = sublime.FocusRestorer()
        self.readyIE()
        self.procQ = processors.WorkerQueue(self.ie)
        self.initHTML(view)

    def reset(self):
        self.ie = self.visible = self.currentFile = None
        self.headRegion = sublime.Region(0, 0)
        if self.procQ: self.procQ.stop()
        print 'Garbage collection', gc.collect()

    def initHTML(self, view):
        self.syntax = view.option.syntax
        self.findHead(view)
        self.buffer(view)

        fn = view.fileName()
        if fn:
            if fn == self.currentFile: return
            else: self.currentFile = fn

        self.ie.navigate(fn or 'about:blank')

    def findHead(self, view):
       head = headRe.search(view.buffer)
       if head: self.headRegion = sublime.Region(*head.span(1))

    def isActive(self):
        return self.ie and (self.ie.isAlive() or self.reset())

    @whenActive
    def onPostSave(self, view):
        if view.fileName(): self.ie.refresh()
        if self.syntax in processors.markups:
            self.buffer(view)

    @whenActive
    @sublimeplugin.onIdle(TIMEOUT)
    def onActivated(self, view):
        self.activateView(view)

    def activateView(self, view):
        self.initHTML(view)

    @whenActive
    @sublimeplugin.onIdle(TIMEOUT)
    def onModified(self, view):
        self.buffer(view)

    def onProcQ(self, buf):
        self.procQ.put(processors.markups[self.syntax], buf)

    def buffer(self, view):
        buf = view.buffer

        if self.syntax in processors.markups:
            return self.onProcQ(buf)

        sel = view.sel()[0]
        cursorInHead = self.headRegion.contains(sel) and sel.end() != 0
        (self.ie.write if cursorInHead else self.ie.buffer)(buf)

################################################################################