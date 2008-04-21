import sublime, sublimeplugin, packagedownloader, threading
from functools import partial

class DownloadPackagesOnSublimeTextWikiCommand(sublimeplugin.ApplicationCommand):
  name = "Package Downloader"
  
  def getPackages(self):
    packageList = packagedownloader.downloadPackages()
    
    # Interrupt main thread to notify          
    sublime.setTimeout(partial(self.notify, packageList), 1)
    
  def notify(self, packageList):
    if len(packageList) == 0: 
      msg = "No Packages Downloaded"
      
    else:
      msg = ("Downloaded these packages;%sPackages will be installed next time "
             "you start Sublime Text." % ("\n\n%s\n\n" % "\n".join(packageList)))
                               
    sublime.messageBox(msg)
    
  def run(self, args):
    sublime.statusMessage("Downloading Packages")
    threading.Thread(target=self.getPackages).start()