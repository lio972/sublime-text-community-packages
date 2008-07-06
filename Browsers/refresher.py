# coding: utf8

################################## IMPORTS #####################################

from __future__ import with_statement
from contextlib import contextmanager

import sublime, sublimeplugin

from absoluteSublimePath import addSublimePackage2SysPath
addSublimePackage2SysPath('Browsers')

from firefox import FireFox, check_mozlab_installed
from iexplore import IE

################################## SETTINGS ####################################

SYNC_EVERY = 0    # seconds, 0 for don't sync

DEBUG = 1

START_URL =  'http://www.google.com.au'

################################################################################

@contextmanager
def errorHandling(self, msg):
    try:
        yield
    except Exception, e:
        self.ie = self.ff = 0
        if DEBUG:
            print msg, e

################################################################################

class BrowsersCommand(sublimeplugin.TextCommand):
    ie = ff = alternation = 0

    def run(self, view, args):
        self.restoreFocus = sublime.FocusRestorer()

        if not self.ie or not self.ff:
            self.readyIE()

            if self.readyFireFox():
                self.navigateTo(START_URL)
                sublime.setTimeout(self.syncBrowsers, 200)
            else:
                if DEBUG: "Can't connect to firefox"
        else:
            with errorHandling(self, 'reInit: '):
                if 'alternate' in args:      self.alternateBrowsers()
                elif 'currentFile' in args:  self.navigateTo(view.fileName())
                else:                        self.toggleVisibility()

        self.restoreFocus()

    def readyIE(self):
        self.ie = IE()
        self.ie.ToolBar = not SYNC_EVERY
        self.ie.Visible = True

    def navigateTo(self, url):
        if url:
            self.ie.Navigate(url)
            self.ff.Navigate(url)

    def readyFireFox(self):
        self.ff = FireFox()
        return self.ff.connection or check_mozlab_installed(sublime)

    def toggleVisibility(self):
        self.ie.Visible = not self.ie.Visible
        self.ff.write (
            "restore()" if self.ie.Visible else 'minimize()', 1
        )

    def alternateBrowsers(self):
        (self.ff if self.alternation % 2 == 0 else self.ie).activate()
        self.alternation += 1

    def refreshBrowsers(self):
        with errorHandling(self, 'refreshBrowsers: '):
            self.ff.Refresh()
            self.ie.Refresh()
    
    def syncBrowsers(self):
        with errorHandling(self, 'syncBrowsers: '):
            firefox_url = self.ff.lastUrl

            if firefox_url != self.ie.LocationURL:
                self.ie.Navigate(firefox_url)
    
            if SYNC_EVERY:
                sublime.setTimeout(self.syncBrowsers, SYNC_EVERY * 1000)

    def onPostSave(self, view):
        if self.ie: self.refreshBrowsers()
        
################################################################################