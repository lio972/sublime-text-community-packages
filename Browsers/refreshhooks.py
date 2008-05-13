################################# IMPORTS ####################################

from __future__ import with_statement
import time, os

################################ SYNCRONISATION ################################

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

##################################### HOOKS ####################################

def apacheRestart(view, lock):
    t = time.time()
    os.popen("psservice stop apache2")
    
    for x in range(100):
        f = os.popen("psservice start apache2")
        f.seek(0)
        if not "Error starting apache2" in f.read(): break
        time.sleep(0.1)
        f.close()
    
    f.close()
    print "apacheRestart: %s seconds" % (time.time() - t)

################################### FILTERS ####################################

def djangoProjects(view, lock):
    with blockMain(lock):
        fn = view.fileName()
    
    if fn.startswith('D:\\django-projects') or fn.endswith('httpd.conf'):
        return True
    
################################################################################