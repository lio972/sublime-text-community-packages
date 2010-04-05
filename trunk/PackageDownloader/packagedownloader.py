#
# package downloader
#

import sys, os, urllib, _winreg


class FakeFile:
  content = ""
  def write(self, block):
    self.content += block

def getUrl(url):
  fl = FakeFile()
  downloadUrl(url, fl)
  return fl.content

def downloadUrl(url, writer):
  package = urllib.urlopen(url)
  for block in readIter(package):
    writer.write(block)
  package.close()
  
def readIter(f, blocksize=8192):
  """Given a file 'f', returns an iterator that returns bytes of
  size 'blocksize' from the file, using read()."""
  while True:
    data = f.read(blocksize)
    if not data: break
    yield data

def progFilesDir():
  progFiles32 = "c:\\program files"
  progFiles64 = "c:\\program files (x86)"
  if os.path.exists(progFiles64): return progFiles64
  if os.path.exists(progFiles32): return progFiles32
  return None

def packageDir():
  Hive = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
  Key = _winreg.OpenKey(Hive, "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
  _winreg.CloseKey(Hive)
  for i in range(0, _winreg.QueryInfoKey(Key)[1]):
    name, value, val_type = _winreg.EnumValue(Key, i)
    if name == "AppData":
      candidate = os.path.join(value, "Sublime Text", "Packages")
      if os.path.exists(candidate):
        return candidate

  return None
  
def packageRoot():
  return "http://sublime-text-community-packages.googlecode.com/svn/packages/"

def listPackages():
  packageList = getUrl(packageRoot() + "all.sublime-distro")
  packageLines = [ line for line in packageList.split("\n") if line.strip() != ""]
  packageNames = [ os.path.splitext(line)[0] for line in packageLines ]
  packageNames.sort()
  return packageNames

def downloadPackages():
  print "SublimeTextWiki.com Package Downloader"
  
  packageContainerUrls = [ 
    "http://sublime-text-community-packages.googlecode.com/svn/packages"
    ]
  
  completedPackageNames = []
  
  
  for packageUrl in packageContainerUrls:
    print "Getting package list from " + packageUrl
    packageList = getUrl(packageUrl)
    packageNames = [ line for line in packageList.split("\n") if line.strip() != ""]
    for package in packageNames:
      downloadLink = packageUrl + "/" + package
      destination  = os.path.join(progFilesDir(), "Sublime Text\\Pristine Packages", package)
      print "Downloading %s from %s to %s..." % (package, downloadLink, destination)
      downloadSinglePackage(downloadLink, destination)
      completedPackageNames.append(package)
      print "...Downloaded to %s" % destination
  
  print "done"
  return completedPackageNames
  
def downloadSinglePackage(downloadLink, destination):
    downloadFile = open(destination, 'wb')
    downloadUrl(downloadLink, downloadFile)
    downloadFile.close()    