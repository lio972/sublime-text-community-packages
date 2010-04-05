#!/usr/bin/python -u
import sys, os, subprocess, traceback, datetime, util, zipfile, googlecode_upload
from string import Template
from fnmatch import fnmatch
from os.path import basename, dirname, join, normpath

print "Content-type: text/plain\n\n"

root    = util.root
site    = util.site
gcode   = "http://sublime-text-community-packages.googlecode.com/svn/trunk/"

dest    = site + "/packages/"
pages   = site + "/pages"
svn     = "svn"
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
  html = util.processMarkdown(readmeContent)
  pageContent = template.substitute(dict(pluginname=dirName, content=html))
  util.saveFile(currentFile, pageContent)
  print "wrote web page for %s to %s" % (dirName, currentFile)
    
    
def create_package(folder_abs, pkgPath, ignore_dirs=(), ignore_files=()):
    """ Takes a `folder_abs` absolute path to a folder and will create a
        sublime-package of same name in the.parent.folders directory.
    """
    pkg = zipfile.ZipFile(pkgPath, 'w')

    for pth, dirs, files in os.walk(folder_abs, topdown=True):

        for ig in ignore_dirs:
            if ig in dirs:
                del dirs[dirs.index(ig)]

        for file_name in files:
            for i in ignore_files:
              if fnmatch(file_name,i):
                continue

            f = normpath(join(pth, file_name))
            pkg.write( f, arcname= f[len(normpath(folder_abs))+1:] )


    pkg.close()

def zipDirectory(dirName, root, dest):
  pathToPackageFiles = os.path.join(root, dirName) 
  zipFileName = dirName + ".sublime-package"
  zipBuildPath = os.path.join(root, zipFileName)
  zipDestPath = os.path.join(dest, zipFileName)
  create_package (
    folder_abs = pathToPackageFiles, 
    pkgPath=zipDestPath,
    ignore_dirs = ('.hg','.svn'),
    ignore_files=['*.pyc', '.hgignore'])
  #os.rename(zipBuildPath, zipDestPath)

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
  allPackagesContent = ""
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
      allPackagesContent = allPackagesContent + dirName + ".sublime-package\n\n"
    
  included.sort()
  homepageList = "\n".join(["<li><a href=\"pages/%s.html\">%s</a></li>\n" % (dirName, dirName)   for dirName in included]) 
  print "%s packages built" % built
  print "The main distribution for PackageDownloader will comprise;"
  print mainDistributionCOntents
  f = open(os.path.join(dest, "main.sublime-distro"), 'w')
  f.write(mainDistributionCOntents)
  f.close()
  
  f = open(os.path.join(dest, "all.sublime-distro"), 'w')
  f.write(allPackagesContent)
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
