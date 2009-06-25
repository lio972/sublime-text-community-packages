import sublime, sublimeplugin, packagedownloader, threading, zipfile, sys, os, shutil
from functools import partial

# class DownloadPackagesOnSublimeTextWikiCommand(sublimeplugin.ApplicationCommand):
#   name = "Package Downloader"
#   
#   def getPackages(self):
#     packageList = packagedownloader.downloadPackages()
#     
#     # Interrupt main thread to notify          
#     sublime.setTimeout(partial(self.notify, packageList), 1)
#     
#   def notify(self, packageList):
#     if len(packageList) == 0: 
#       msg = "No Packages Downloaded"
#       
#     else:
#       msg = ("Downloaded these packages;%sPackages will be installed next time "
#              "you start Sublime Text." % ("\n\n%s\n\n" % "\n".join(packageList)))
#                                
#     sublime.messageBox(msg)
#     
#   def run(self, args):
#     sublime.statusMessage("Downloading Packages")
#     threading.Thread(target=self.getPackages).start()
    
class BrowsePackagesOnSublimeTextWikiCommand(sublimeplugin.WindowCommand):
  
  def getPackages(self):
    packageList = packagedownloader.listPackages()
    
    # Interrupt main thread to notify          
    sublime.setTimeout(partial(self.notify, packageList), 1)

  def notify(self, packageNames):
    
    self.window.showQuickPanel("", "packageSelectedForInstallation", packageNames, packageNames, sublime.QUICK_PANEL_MULTI_SELECT)
        
  def run(self, window, args):
    self.window = window
    sublime.statusMessage("Downloading Packages")
    threading.Thread(target=self.getPackages).start()


class PackageSelectedForInstallationCommand(sublimeplugin.TextCommand):
 
  def run(self, view, args):
    if len(args) == 0:
      sublime.messageBox("You didn't select anything.")
    else:
      name = args[0]      
      url = packagedownloader.packageRoot() + name + ".sublime-package"
      answer = sublime.questionBox("Download '%s'?" % url)   
      if answer:
        localPackageRoot = packagedownloader.packageDir()
        if localPackageRoot == None:
          sublime.messageBox("Could not find package folder. Sorry.")
          return
        destination = "c:/downloaded-by-sublime-text-package-downloader.sublime-package"
        packagedownloader.downloadSinglePackage(url, destination)
        
        packageFolder = os.path.join(localPackageRoot, name)
        
        existsAlready = ""
        if os.path.exists(packageFolder):
          existsAlready = " This folder already exists and will be replaced."
        
        unpackAnswer = sublime.questionBox("Download succeeded. Do you wish to install in '%s'?%s " % (packageFolder, existsAlready))
        if not unpackAnswer:
          os.remove(destination)
          return
        
        self.expandPackage(destination, packageFolder)
        os.remove(destination)
        sublime.messageBox("Unpacked to %s" % packageFolder)

  def expandPackage(self, zipPath, destinationFolder):
    if os.path.exists(destinationFolder):
      # must delete existing path.
      shutil.rmtree(destinationFolder)
    os.mkdir(destinationFolder)
    zfobj = zipfile.ZipFile(zipPath)
    for name in zfobj.namelist():
        if name.endswith('/'):
            d = os.path.join(destinationFolder, name)
            os.mkdir(d)                        
        else:
            file = os.path.join(destinationFolder, name)
            outfile = open(file, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()
