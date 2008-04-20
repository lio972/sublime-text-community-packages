import sublime, sublimeplugin, packagedownloader, threading
from functools import partial

class DownloadPackagesOnSublimeTextWikiCommand(sublimeplugin.ApplicationCommand):
  name = "Package Downloader"
  
  def getPackages(self):
    packageList = packagedownloader.downloadPackages()    
    sublime.setTimeout(partial(self.notify, packageList), 1)
    
  def notify(self, packageList):
    if len(packageList) == 0:
      msg = "No Packages Downloaded"
    
    else:  
      packages = "\n".join(packageList)
      msg = "Downloaded these packages;\n\n  " + packages +\
             "\n\nPackages will be installed next time you start Sublime Text."
             
    sublime.messageBox(msg)
    
  def run(self, args):
    sublime.statusMessage("Downloading Packages")
    t = threading.Thread(target=self.getPackages)
    t.start()
    