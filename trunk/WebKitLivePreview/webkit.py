#################################### IMPORTS ###################################

import sublime, sublimeplugin, threading, time, Queue

from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView

################################### SETTINGS ###################################
      
DEBUG = 0

################################### COMMANDS ###################################

ToggleVisibility = object()

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
      self.Q.put(ToggleVisibility)
                          
  def QtLoop(self):    
    app = QApplication([])
    
    browser = QWebView()
    browser.show()
    
    i = 0
    while True:
      i += 1
      try:
        packet = self.Q.get_nowait()
        if packet:
          if packet is ToggleVisibility:
            if browser.isVisible():
              browser.hide()
            else:
              browser.show()
          else:
            browser.setHtml(packet)
            if DEBUG: print packet[:100]
            
      except Queue.Empty:
        time.sleep(0.001)

      app.processEvents()
    
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