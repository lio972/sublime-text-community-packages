#
# package downloader
#

import sys, os, urllib

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
  progFiles64 = "c:\\program files (x86)"
  progFiles32 = "c:\\program files"
  if os.path.exists(progFiles64): return progFiles64
  if os.path.exists(progFiles32): return progFiles32
  return None

def downloadPackages():
  print "SublimeTextWiki.com Package Downloader"
  
  packageContainerUrls = [ 
    "http://www.sublimetextwiki.com/sublime-packages"
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
      downloadFile = open(destination, 'wb')
      downloadUrl(downloadLink, downloadFile)
      downloadFile.close()
      completedPackageNames.append(package)
      print "...Downloaded to %s" % destination
  
  print "done"
  return completedPackageNames