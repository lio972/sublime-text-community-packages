from functools import partial
import sublime, time, sys, os

pkgPath = os.path.join(sublime.packagesPath(), "Browsers")
sys.path.append(pkgPath + "\\Lib")

from comtypes.client import CreateObject                  
ie = CreateObject("InternetExplorer.Application")
ie.Visible = 1
ie.Navigate('www.sublimetext.com')


sublime.messageBox("comtypes needs to create the bindings for InternetExplorer\n"
                   "This is a one time thing, but will take maybe a minute\n\n"
                   "Press OK when InternetExplorer has loaded\n\n"
                   "NOTE: SUBLIME MAY APPEAR STALLED")
time.sleep(1)                
                   
doc = ie.Document
ie.Document.getElementsByTagName("h1")[0].innerHTML = "WORKOUT COMPLETE"

sublime.setTimeout(partial(os.rename, os.path.join(pkgPath, "comtypes_workout.py"),
           os.path.join(pkgPath, "comtypes_workout.done")),  1000)

