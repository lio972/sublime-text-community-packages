#################################### IMPORTS ###################################

import sublime, sublimeplugin, threading, time, Queue

from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView

################################### SETTINGS ###################################
      
DEBUG = 0

################################### COMMANDS ###################################

TOGGLE_VISIBILITY, DIE = object(), object()

#################################### README ####################################

"Note: (on Windows at least) PyQt4.4 rc1, as opposed to PyQt4.3 stable, no "
"longer works running multiple QApplications at once or even more than one "
"per sublime session. (In different threads, single threaded apps with the "
"QApplication in the main thread still seem to work, though not at the same "
"time. Maybe it would be best to set up a live preview window in another "
"process listening on a socket for packets. Better yet, a native sublime "
"widget. WebKit embedded. Consult your local member."

################################ PYQT4 MAIN LOOP ###############################

class QtMain(threading.Thread):
  def __init__(self, Q):
    self.Q = Q
    threading.Thread.__init__(self)
  
  def run(self):
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
             (browser.hide if browser.isVisible() else browser.show)()
          elif packet is DIE: break
          else:
            browser.setHtml(packet)
            if DEBUG: print packet[:100]
  
      except Queue.Empty:
        time.sleep(0.01)
  
      app.processEvents()
      if DEBUG and i % 10: print i

#################################### COMMAND ###################################

class WebkitCommand(sublimeplugin.TextCommand):
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
      self.Q.put(TOGGLE_VISIBILITY)
      
  def stop(self):
    self.Q.put(DIE)
    self.started = False
  
  def start(self):
    self.started, self.visible = True, True
    QtMain(self.Q).start()

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