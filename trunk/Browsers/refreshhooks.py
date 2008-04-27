################################### IMPORTS ####################################

from __future__ import with_statement
import time, os
from threading import Semaphore, Lock, RLock

##################################### HOOKS ####################################

def apacheRestart(view):
    t = time.time()
    os.popen("psservice stop apache2")
    
    for x in range(100):
        f = os.popen("psservice start apache2")
        f.seek(0)
        ret = f.read()
        if not "Error starting apache2" in ret: break
        time.sleep(0.1)
        f.close()
    
    f.close()
    print "apacheRestart: %s seconds" % (time.time() - t)

################################### FILTERS ####################################

def djangoProjects(view):
    "Acquire and release a blocking lock so can get view fileName" 
    with RLock(): fn = view.fileName()
    
    return fn.startswith('D:\\django-projects')
    
################################################################################