#################################### IMPORTS ###################################

from __future__ import with_statement

from absoluteSublimePath import addSublimePackage2SysPath

from functools import partial

import sublime, sublimeplugin, threading, time

addSublimePackage2SysPath('PyQt4Experimental')
        
################################### SETTINGS ###################################
      
DEBUG = 1
        
################################ SYNCRONISATION ################################

def blockQtAndDo(lock, func, *args, **kw):
  sublime.setTimeout(lock.acquire, 0)
  func(*args, **kw)
  sublime.setTimeout(lock.release, 0)

class blockMain(object):
  def __init__(self, lock):
    self.lock = lock
    self.acquired = False

  def __enter__(self):
    self.lock.acquire()
    sublime.setTimeout(self.lock.acquire, 0)
    self.acquired = True

  def __exit__(self, *exc):
    if self.acquired:
      sublime.setTimeout(self.lock.release, 0)
      self.lock.release()
      self.acquired = False
  
#################################### COMMAND ###################################

class TestGuiCommand(sublimeplugin.TextCommand):
  app = None
  started = False
  lock = threading.RLock()
    
  def run(self, view, args):
    self.view = view
    
    if 'STOP' in args: 
      self.die, self.started = True, False
      return
    
    if not self.started:
      self.die, self.started = False, True
      threading.Thread(target=self.QtLoop).start()
    else:
        # This will stall Sublime
        
        # self.lock.acquire()
        # self.form.show()
        # self.lock.release()
                      
      blockQtAndDo(self.lock, self.form.show)
                          
  def setRuler(self, val):
    self.view.options().set('rulers', val)
  
  def QtLoop(self):
    # Import in thread so doesn't slow down sublime startup
    from qtform import QApplication, Ruler
    
    self.app = QApplication([])
    self.form = Ruler(self)

    # How to block the main thread temporarily?
    # to safely run view.function()
    with blockMain(self.lock):
      self.form.rulers.setValue(self.view.options().get('rulers') or -1)
      
    self.form.show()
        
    i = 0
    while True:
      i += 1
      
      with self.lock:
        self.app.processEvents()
      
      time.sleep(0.02)
      
      if i % 10 == 0:
        if DEBUG: print i         
        if self.die: break
            
    del(self.app, self.form)
  
  def onActivated(self, view):
    if self.app:
      self.view = view
      
      #TODO: ????     How long to block thread 4 ?
      # Not really needed here? 
      with self.lock:
        self.form.rulers.setValue(self.view.options().get('rulers') or -1)
  
  def onPreSave(self, view):
    if self.app:
      view.runCommand('testGui STOP')    
        
################################################################################