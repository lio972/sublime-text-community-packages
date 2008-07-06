# coding: utf8

################################## IMPORTS #####################################

from __future__ import with_statement

import sublime, sublimeplugin, re,  functools

from absoluteSublimePath import addSublimePackage2SysPath
addSublimePackage2SysPath(u'Browsers')

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
    def isActive(self, *args, **kwargs):
        if self.isActive() and self.visible:
            func(self, *args, **kwargs)
    return isActive

################################################################################

class LivePreviewCommand(sublimeplugin.TextCommand):
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
        self.initHTML(view)

    def reset(self):
        self.ie = self.visible = self.currentFile = None
        self.headRegion = sublime.Region(0, 0)

    def initHTML(self, view):
        fn = view.fileName()
        self.syntax = view.option.syntax

        self.findHead(view)
        self.buffer(view)

        if fn:
            if fn == self.currentFile: return
            else: self.currentFile = fn

        self.ie.navigate(fn or 'about:blank')

    def findHead(self, view):
       head = headRe.search(view.buffer)
       if head:
           self.headTag = head.group(1)
           self.headRegion = sublime.Region(*head.span(1))                                      

    def isActive(self):
        if self.ie:
            return self.ie.isAlive() or self.reset()

    @whenActive
    def onPostSave(self, view):
        if view.fileName(): self.ie.refresh()
        if self.syntax in processors.markups:
            self.buffer(view)

    @whenActive
    def onActivated(self, view):
        self.activateView(view)
    
    @sublimeplugin.onIdle(TIMEOUT)
    def activateView(self, view):
        self.initHTML(view)
    
    @whenActive
    @sublimeplugin.onIdle(TIMEOUT)
    def onModified(self, view):
        self.buffer(view)

    def buffer(self, view):
        buf = view.buffer
        fn = view.fileName()

        sel = view.sel()[0]
        cursorInHead = self.headRegion.contains(sel) and sel.end() != 0
        (self.ie.write if cursorInHead else self.ie.buffer)(buf)

################################################################################