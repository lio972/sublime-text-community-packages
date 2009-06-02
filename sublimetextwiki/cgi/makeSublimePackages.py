#!/usr/bin/python -u
import sys, os, subprocess, traceback, markdown, datetime, util
from string import Template

print "Content-type: text/plain\n\n"

root    = util.root
site    = util.site
gcode   = "http://sublime-text-community-packages.googlecode.com/svn/trunk/"

dest    = site + "/sublime-packages/"
pages   = site + "/pages"
svn     = "/usr/bin/svn"
args    = "co %s %s" % (gcode, root)
cmdline = "%s %s" % (svn, args)

def getFromSvn():
  print "getting packages from SVN\n"
  util.run([svn, "up", gcode, root], root)
  
def packageDirs(dirName):
  result = []
  dirs  = os.listdir(dirName)
  for partialPath in dirs:
    fullPath = os.path.join(dirName,partialPath) 
    if os.path.isdir(fullPath) and partialPath.startswith(".") == False:
      result.append(partialPath)
  return result

def filenameForPackagePage(dirName, dest):
  """The unix filename for the HTML page describing the package"""
  return os.path.join(dest, dirName + ".html")

def getReadmeFile(root, dirName):
  readmeFile = os.path.join(root, dirName , "README.txt")
  return readmeFile
  
def copyReadmeFile(dirName, root, dest):
  readmeFile = getReadmeFile(root, dirName)
  currentFile = filenameForPackagePage(dirName, dest)
   
  if os.path.exists(readmeFile):
    readmeContent = util.loadFile(readmeFile)
  else:
    readmeContent = "This package does not have a README.txt file. If you are the developer, please add one to improve this page. The file should be written in [Markdown](http://daringfireball.net/projects/markdown/)"
    
  template = Template(util.loadFile("../templates/package.template.html"))
  html = markdown.markdown(readmeContent)
  pageContent = template.substitute(dict(pluginname=dirName, content=html))
  util.saveFile(currentFile, pageContent)
  print "wrote web page for %s to %s" % (dirName, currentFile)
    
def zipDirectory(dirName, root, dest):
  print "Zipping %s\n" % dirName
  pathToPackageFiles = os.path.join(root, dirName) 
  
  zipFileName = dirName + ".sublime-package"
  zipBuildPath = os.path.join(root, zipFileName)
  zipDestPath = os.path.join(dest, zipFileName)
  
  print "zipping all files to %s"  % zipBuildPath
  util.run(["zip", "-r", zipBuildPath, ".", "-x", "*.svn*"], pathToPackageFiles)
  
  print "moving file from %s to %s" % (zipBuildPath, zipDestPath)
  os.rename(zipBuildPath, zipDestPath)

def partOfMainDistribution(packageDir, root):
  """Is this part of the main set of files to download?"""
  pathToPackageFiles = os.path.join(root, dirName) 
  mainMarker = os.path.join(
    pathToPackageFiles, 
    "main.sublime-distro")
  return os.path.exists(mainMarker)
  
def shouldBeBuilt(packageDir, root): 
  """should we build this package directory? The developer can mark 
  a package as invisible by putting an appropriate marker file into SVN"""
  pathToPackageFiles = os.path.join(root, dirName) 
  dontBuildMarker = os.path.join(
    pathToPackageFiles, 
    "not-for-distribution.sublime-distro")
  return os.path.exists(dontBuildMarker) == False

 
  
try:
  print "Building\n"
  mainDistributionCOntents = ""
  getFromSvn()
  included = []
  dirNames = packageDirs(root)
  built = 0
  for dirName in dirNames:
    if (shouldBeBuilt(dirName, root)):
      built = built+1
      zipDirectory(dirName, root, dest)
      copyReadmeFile(dirName, root, pages)
      included.append(dirName)
      if (partOfMainDistribution(dirName, root)):
        mainDistributionCOntents = mainDistributionCOntents + dirName + ".sublime-package\n\n"
    
  included.sort()
  homepageList = "\n".join(["<li><a href=\"pages/%s.html\">%s</a></li>\n" % (dirName, dirName)   for dirName in included]) 
  print "%s packages built" % built
  print "The main distribution for PackageDownloader will comprise;"
  print mainDistributionCOntents
  f = open(os.path.join(dest, "main.sublime-distro"), 'w')
  f.write(mainDistributionCOntents)
  f.close()
  
  today = datetime.datetime.now().ctime()
  template = Template(util.loadFile("../templates/index.template.html"))
  homepage = template.substitute(dict(packagelist=homepageList, today=today))
  util.saveFile(os.path.join(site, "index.html"), homepage)
  print "Done. Please hit the 'back' button on your browser to browse the new pages."
  
except:
  exc_info = sys.exc_info()
  print exc_info[0]    
  print exc_info[1]
  traceback.print_tb(exc_info[2])    
