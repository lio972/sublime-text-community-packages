#################################### IMPORTS ###################################

from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import sublime, sublimeplugin, threading, time, Queue

################################### SETTINGS ###################################
      
DEBUG = 0

################################### COMMANDS ###################################

SHOW = object()

HIDE = object()

#################################### README ####################################

"Note: (on Windows at least) PyQt4.4 rc1, as opposed to PyQt4.3 stable no "
"longer works running multiple QApplications at once or even more than one "
"per sublime session. There are paint issues "

#################################### COMMAND ###################################

class WebkitCommand(sublimeplugin.TextCommand):
  """ Webkit for LivePreview """
  started = False
  visible = False
  
  Q = Queue.Queue()
  
  def run(self, view, args):
    self.view = view

    if 'STOP' in args: 
      self.die, self.started = True, False
      return
    
    if not self.started:
      self.die, self.started, self.visible = False, True, True
      threading.Thread(target=self.QtLoop).start()
    else:
      self.visible = not self.visible
      self.Q.put(HIDE if self.visible else SHOW)
                          
  def QtLoop(self):    
    app = QApplication([])
    
    browser = QWebView()
    browser.show()
    
    i = 0
    while True:
      i += 1
      
      app.processEvents()
      try:
        packet = self.Q.get_nowait()
        if packet:
          if packet is SHOW:
            browser.show()
          elif packet is HIDE:
            browser.hide()
          else:
            browser.setHtml(packet)
            if DEBUG: print packet[:100]
            
      except Queue.Empty:
        time.sleep(0.001)
            
      if i % 100 == 0:
        if DEBUG: print i
        if self.die:
          break
        
    del(app, browser)
  
  def onActivated(self, view):
    if self.started and self.visible:
      self.Q.put_nowait(view.substr(sublime.Region(0, view.size())))
  
  def onModified(self, view):
    if self.started and self.visible:
      self.Q.put_nowait(view.substr(sublime.Region(0, view.size())))
    
  def onPreSave(self, view):
    if DEBUG and self.started:
      view.runCommand('webkit STOP')    
        
################################################################################