# coding: utf8

import sublimeplugin, webbrowser, time, re, os, sys, sublime
from subprocess import Popen

from absoluteSublimePath import addSublimePackage2SysPath

addSublimePackage2SysPath(u'Browsers')

from ctypes import windll
from comtypes.client import CreateObject
from telnetlib import Telnet
from functools import partial

from windows import FocusRestorer, activateApp

debug = 0
MozLabURL = "http://repo.hyperstruct.net/mozlab/current/mozlab-current.xpi"

FFLastUrl = re.compile('"(.*?://.*?)".*repl[0-9]?', re.DOTALL | re.MULTILINE)
   
class BrowsersCommand(sublimeplugin.TextCommand):
    ie = None
    firefox = None
    alternation = 0
    firefoxHWND = 0
        
    def readyIE(self):
        self.ie = CreateObject("InternetExplorer.Application")
        self.ie.ToolBar = 0
    
    def readyFireFox(self, url):    
        cmd = r'"C:\Program Files\Mozilla Firefox\firefox.exe" -new-tab %s'
        Popen(cmd % 'www.google.com.au')
        
        for x in range(50):   #Try for 10 seconds
            try:
                self.firefox = Telnet('localhost', 4242)
                break
            except:
                time.sleep(0.2)
            
        if self.firefox: return True
                            
        question =("This plugin requires firefox open and MozLab intalled\n"
                   "Do you need to download MozLab ?")
        
        if sublime.questionBox(question):
            try: webbrowser.open(MozLabURL)
            except WindowsError:
                sublime.setClipboard(MozLabURL)
                sublime.messageBox("Tried browsing to MozLab\n"
                                   "Url also in clipboard")
                
    def syncBrowsers(self, only_sync=False):
        #IE has no toolbars and follows firefoxs lead
        try:
            self.firefox.read_very_eager()
                    
            self.firefox.write('gLastValidURLStr\n')
            output = self.firefox.read_until('repl', 5)
                            
            for url in FFLastUrl.findall(output):
                if url == self.ie.LocationURL:
                    if not only_sync: 
                        self.ie.Refresh()
                else:
                    self.ie.Navigate(url)
        
        except Exception, e:
            if debug: print 'syncBrowsers: ', e
                
        sublime.setTimeout(partial(self.syncBrowsers, only_sync = True), 2000)
        
    def run(self, view, args):
        restoreFocus = FocusRestorer()
        
        fn  = view.fileName()
        if fn: curFile = 'file:///' + fn.replace('\\','/')
        else: curFile = ''
            
        if not self.ie or not self.firefox:
            self.readyIE()
            self.ie.Visible = True
            
            if self.readyFireFox(curFile):
                if curFile.endswith(('html','htm')):
                    cmd = str("openTopWin('%s')\n" % curFile)
                    self.firefox.write(cmd)
                
                sublime.setTimeout(self.syncBrowsers, 200)
                    
        else: 
            try:
                if 'alternate' in args:
                    self.alternateBrowsers()
                else:
                    self.ie.Visible = not self.ie.Visible
    
                    cmd = "restore" if self.ie.Visible else 'minimize'
                    self.firefox.write('%s()\n' % cmd)
                                                   
            except Exception, e:
                self.ie = None
                self.firefox = None
                if debug: print 'reInit: ', e
        
        sublime.setTimeout(restoreFocus, 50)

    def alternateBrowsers(self):
        restoreFocus = FocusRestorer()
        
        self.firefoxHWND = self.firefoxHWND or activateApp(
                        "MozillaUIWindowClass",
                        '.*Mozilla Firefox.*'
        )
 
        h = self.firefoxHWND if self.alternation % 2 == 0 else self.ie.HWND
        
        windll.user32.SetForegroundWindow(h)
        
        sublime.setTimeout(restoreFocus, 1)
        self.alternation += 1
                                    
    def onPostSave(self, view):
        try:
            if self.ie and self.ie.Visible:
                self.firefox.write('BrowserReloadWithFlags(16)\n')
                self.syncBrowsers()
                # sublime.setTimeout(self.alternateBrowsers, 3000)
                                             
        except Exception, e: 
            if debug: print 'onPostSave: ', e