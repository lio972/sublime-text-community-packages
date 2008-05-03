#################################### IMPORTS ###################################

import sublime, sublimeplugin, threading, time, Queue, random, gc

from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView

################################### SETTINGS ###################################
      
DEBUG = 0

################################### COMMANDS ###################################

def QCommand(): return object()

TOGGLE_VISIBILITY, DIE = QCommand(), QCommand()

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
    if 'STOP' in args:
      self.stop()
      return
      
    if not self.started:
      self.start()
    else:
      if 'STOP' in args:
        self.stop()
        return
      else:
        self.Q.put(TOGGLE_VISIBILITY)
  
  def stop(self):
    self.Q.put(DIE)
    self.started = False
  
  def start(self):
    self.started, self.visible = True, True
    threading.Thread(target=self.QtLoop).start()
                          
  def QtLoop(self):
    app = QApplication([])
    
    browser = QWebView()
    browser.show()
    browser.resize(1024, 600)
    browser.setWindowTitle('WebKit Live Preview')
    
    i = 0
    while True:
      i += 1
      try:
        packet = self.Q.get_nowait()
        if packet:
          if packet is TOGGLE_VISIBILITY:
            if browser.isVisible():
              browser.hide()
            else:
              browser.show()
          elif packet is DIE:
            break
          else:
            browser.setHtml(packet)
            if DEBUG: print packet[:100]
            
      except Queue.Empty:
        time.sleep(0.001)

      app.processEvents()
    
      if i % 100 == 0:
        if DEBUG: print i
                
    del(app, browser)
    gc.collect()
  
  def sendBuffer(self, view):
    self.Q.put_nowait(view.substr(sublime.Region(0, view.size())))
    
  def onActivated(self, view):
    if self.started and self.visible:
      self.sendBuffer(view)  
  
  def onModified(self, view):
    if self.started and self.visible:
      self.sendBuffer(view)
    
  def onPreSave(self, view):
    if DEBUG and self.started:
      self.stop()
        
################################################################################