# coding: utf8

from __future__ import with_statement

from absoluteSublimePath import addSublimePackage2SysPath

addSublimePackage2SysPath(u'Browsers')

import sublimeplugin, time, threading, Queue, re, smartypants, textile, os, sys\
     , sublime

from ctypes import windll
from comtypes.client import CreateObject
from comtypes import COMError

from functools import partial

# for markdown2
sys.argv = [] 
import markdown2

### SETTINGS ###

DEBUG = 0
TIMEOUT = 35

# for processing markdown/textile etc
QUEUE_SIZE = 8
NUM_WORKERS = 4

#write buffer to temporary file instead of DOM manipulation
#will not work in "processed" mode
TEMP_MODE = 0

### REGEXES ###

reFlags = re.DOTALL | re.IGNORECASE | re.MULTILINE
headRe = re.compile("(<head.*?>.*?</head>)", reFlags)

processed={}

def proc_markdown(a):
    return smartypants.smartyPants(markdown2.markdown(a))

def proc_textile(a):
    return smartypants.smartyPants(textile.textile(str(a)))

processed["Packages/Markdown/Markdown.tmLanguage"] = proc_markdown
processed['Packages/Textile/Textile.tmLanguage'] = proc_textile

### FUNCTIONS && CLASSES ###

class FocusRestorer(object):
    def __init__(self): 
        self.h = windll.user32.GetForegroundWindow()
    def __call__(self, t=25):  sublime.setTimeout(
            partial(windll.user32.SetForegroundWindow, self.h), t
        )
        
class ThreadedIE(threading.Thread):
    dead = False
    
    def __init__ (self):
        threading.Thread.__init__ (self)
        self.Q = Queue.Queue()
        self.start()

    def run (self):                
        # enable COM multithreading
        windll.ole32.CoInitializeEx(None, 0x2)
        #LATE IMPORTING, SOMETIMES CURRENT DIRECTORY HAS CHANGED
        
        ie = CreateObject('InternetExplorer.Application')
        
        ie.ToolBar = 0
        ie.StatusBar = 0
        ie.Visible = 1
        
        while 1:
            try:
                item = self.Q.get()
                try: command, arg = item
                except ValueError: command = item[0]
            except Queue.Empty:
                time.sleep(0.01)
                continue
                                
            if command:                
                if DEBUG: print 'command: ', command             
                try:    
                    if command == "toggleVisible":
                        restoreFocus = FocusRestorer()
                        ie.Visible = not ie.Visible                
                        restoreFocus()
                        
                    elif command == "navigate":
                        ie.Navigate(arg)
                        while ie.ReadyState != 4:
                            pass
                                    
                    elif command == "write":
                        
                        if ie.ReadyState != 4: pass
                        
                        ie.Document.open()
                        ie.Document.write(arg)
                        ie.Document.close()
                    
                    elif command == "refresh":
                        ie.Refresh()
                    
                    elif command == "buffer":
                        try: 
                            ie.Document.body.innerHTML = arg
                            while ie.ReadyState != 4:
                                pass
                        except:
                            pass
                            
                    self.Q.task_done()
                    
                except Exception, e:
                    self.dead = True
                    if DEBUG:
                        print "Thread break:  %s" % e
                        print "Unfinshed tasks %s" % self.Q.unfinished_tasks
                    break
        
        while 1:
            try: self.Q.task_done() 
            except ValueError: break
                
        try: ie.Quit() 
        except COMError, e: 
            if DEBUG: print "ie.Quit(): %s" % e
        ie = None
        
        windll.ole32.CoUninitialize()
    
    def __call__(self, *args):
        self.Q.put_nowait(args)

STOP = object()
class WorkerThread(threading.Thread):
    def __init__(self, IQ, OQ):
        threading.Thread.__init__(self)
        self.IQ = IQ
        self.OQ = OQ
        self.start()
        
    def run(self):
        i = 1
        while True:
            try:                     
                cmd, item = self.IQ.get()
                if cmd is STOP: 
                    break
                if item:
                    self.OQ.put((cmd, item()))
            except Queue.Empty:
                time.sleep(0.1)
                
        if DEBUG: print "Thread Stop: %s", self.getName()
        return
        
        
### PLUGIN ###

class LivePreviewCommand(sublimeplugin.TextCommand):
    def __init__(self):
        self.workers = []
        self.tempFiles = set()
        self.reset()
        
    def run(self, view, args):
        if not self.ie:
            self.init(view)
        else:
            if self.isActive():
                self.ie('toggleVisible')
                self.visible = not self.visible

                if DEBUG: print 'visible: ', self.visible
                
                time.sleep(0.05)
                if not self.ie.isAlive():
                    self.run(view, args)                    
            else:
                self.run(view, args) 
    
    def readyIE(self):
        restore = FocusRestorer()
        
        self.ie = ThreadedIE() 
        self.visible = True
        
        # IE TAKES TIME TO LOAD
        restore(1)
        restore(750)
        restore(1500)
    
    def stopWorkers(self):
        if self.workers:
            for t in self.workers:
                self.procQ.put((STOP, 0))
    
    def initWorkers(self):
        self.procQ = Queue.Queue(QUEUE_SIZE)
        
        if self.workers and DEBUG:
            for t in self.workers:
                try: print "ALIVE: ", t.isAlive()
                except: pass
            
        self.workers = []
        for _ in range(NUM_WORKERS):
            self.workers.append(WorkerThread(self.procQ, self.ie.Q))
        
    def init(self, view):
        self.readyIE()
        self.initWorkers()
        self.initHTML(view)
    
    def reset(self):
        self.ie = None
        self.visible = False
        self.currentFile = ''
        
        self.pendingMods = 0
        self.pendingActivations = 0
        self.headRegion = sublime.Region(0, 0)
        
        self.stopWorkers()
        
        # TIDY UP TEMP FILES
        for f in self.tempFiles:
            try: os.remove(f)
            except Exception, e:
                print 'Cleanup: ', e
            
    def initHTML(self, view):
        self.syntax = view.options().get('syntax')
        self.findHead(view)
        fn = view.fileName()
        
        self.buffer(view)
        
        if fn and fn == self.currentFile:
            return
        
        self.ie('navigate', fn or 'about:blank')
        
        if fn: self.currentFile = fn
        
    def findHead(self, view):
       buffer = view.substr(sublime.Region(0, view.size()))                
       head = headRe.search(buffer)
       if head:
           self.headTag = head.group(1)
           self.headRegion = sublime.Region(*head.span(1))                                             
        
    def isActive(self):
        if self.ie:
            if not self.ie.dead:
                return True
            else:
                self.reset()
                      
    ### REFRESH ON SAVE ###
    
    def onPostSave(self, view):
        if self.isActive() and self.visible:
            if view.fileName():
                self.ie('refresh')
            
            if self.syntax in processed:
                self.buffer(view)    
    
    ### FOLLOW THE FILE ###            
                
    def onActivated(self, view):
        if self.isActive() and self.visible:
            self.pendingActivations += 1
            sublime.setTimeout(partial(self.activatedIdleTimeout, view), TIMEOUT)
        
    def activatedIdleTimeout(self, view):
        self.pendingActivations  -= 1
        if self.pendingActivations == 0:
            self.activateView(view)
            
    def activateView(self, view):
        self.initHTML(view)
    
    ### BUFFER UPDTATING ###
    
    def onModified(self, view):
        if self.isActive() and self.visible:
            self.pendingMods += 1            
            sublime.setTimeout(partial(self.idleTimeout, view), TIMEOUT)
  
    def idleTimeout(self, view):
        self.pendingMods  -= 1
        if self.pendingMods == 0:
            self.buffer(view)
    
    def buffer(self, view):
        buf = view.substr(sublime.Region(0, view.size()))            
        fn = view.fileName()

        sel = view.sel()[0]
        cursorInHead = self.headRegion.contains(sel) and sel.end() != 0
        
        arg = buf
        if cursorInHead or TEMP_MODE:
            if fn:
                preview = "%s.preview" % fn
                self.tempFiles.add(preview)
                with open(preview, 'w') as fh: fh.write(buf)
                cmd, arg = 'navigate', preview
            else:
                cmd = 'write'
        else:
            cmd = 'buffer'
        
        if self.syntax in processed:
            arg = partial(processed[self.syntax], buf)
            try:
                self.procQ.put_nowait(('buffer', arg))
            except Queue.Full:
                pass
        else:
            self.ie(cmd, arg)