#################################### IMPORTS ###################################

from __future__ import with_statement

import sublime, sublimeplugin, threading, time

from functools import partial

from PyQt4.QtCore import *
from PyQt4.QtGui import *
        
################################### SETTINGS ###################################
        
DEBUG = 1
        
################################## PYQT4 FORM ##################################

class Ruler(QDialog):
  def __init__(self, plugin, parent=None):
    super(Ruler, self).__init__(parent)
    self.plugin = plugin
    
    self.rulers = QSpinBox()
    self.rulers.setRange(-1, 80)
    self.rulers.setValue(80)
    self.rulers.setAccelerated(True)
    self.rulers.setWrapping(True)

    layout = QGridLayout()
    layout.addWidget(self.rulers, 0,0)
    
    self.setLayout(layout)

    self.connect(self.rulers, SIGNAL("valueChanged(int)"), self.updateRuler)
    
  def updateRuler(self):
    " timeOut's are run in blocking call in main thread and are safe to use"

    sublime.setTimeout(
       partial(self.plugin.setRuler, self.rulers.value()), 20
    )

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
    self.app = QApplication([])
    self.form = Ruler(self)

    # How to block the main thread temporarily? 
    # to safely run view.function()
    with blockMain(self.lock):
      # time.sleep(2)
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
      with self.lock:
        self.form.rulers.setValue(self.view.options().get('rulers') or -1)
  
  def onPreSave(self, view):
    if self.app:
      view.runCommand('testGui STOP')    
        
################################################################################