#
# Subversion status
#

import os, subprocess, re, datetime, sublime, sublimeplugin, functools

class SubversionStatusProvider(sublimeplugin.Plugin):  
  """Informs the user of the subversion status of the files they are editing."""
  
  def onLoad(self, view):  
    sublime.statusMessage(SubversionStatus(view))
  
  def onPostSave(self, view):  
    sublime.statusMessage(SubversionStatus(view))
  
  def onNew(self, view):  
    sublime.statusMessage(SubversionStatus(view))
  
  def onModified(self, view):  
    #sublime.statusMessage(SubversionStatus(view))
    pass
    p
  def onActivated(self, view): 
    sublime.statusMessage(SubversionStatus(view))
  
  def onClone(self, view):  
    sublime.statusMessage(SubversionStatus(view))
  
  
def SubversionStatus(view):
  """returns a string describing the subversion status of this file"""

  filename = view.fileName()
  
  # a new file will not have a filename yet.
  if os.path.exists(filename) == False: return "%s not yet saved" % filename

  # the file without directory name, used in building the result
  shortname = os.path.basename(filename)

  # use SVN to find out status
  svnStatus = getOutputOfSysCommand("svn status -v \"%s\"" % view.fileName())

  if (len(svnStatus) == 0): return "%s is NOT UNDER VERSION CONTROL" % shortname

  # use 'svn help status' to find out exactly what's going on here;
  # basically, the first three columns explain the status of the file, 
  # the properties of the file, and the lock status.  
  statusCol   = svnStatus[0]
  propertyCol = svnStatus[1]
  lockCol     = svnStatus[2]
    
  return "%s: %s, %s, %s" % (shortname, statusColDescription(statusCol), propertyColDescription(propertyCol), lockColDescription(lockCol))

def statusColDescription(statusChar):
  """converts the character from SVN into a meaningful message"""
  statusDict = {
      " ": "file NOT MODIFIED",
      "A": "file ADDED",
      "C": "file CONFLICTED",
      "D": "file DELETED",
      "I": "file IGNORED",
      "M": "file MODIFIED",
      "R": "file REPLACED",
      "X": "item is UNVERSIONED, but is used by an externals definition",
      "?": "item is NOT UNDER VERSION CONTROL",
      "!": "item is MISSING (removed by non-svn command) or incomplete",
      "~": "versioned item OBSTRUCTED by some item of a different kind)",
  }
  return statusDict[statusChar]
  
def propertyColDescription(propertyChar):
  """converts the character from SVN into a meaningful message"""
  propertyDict = {
      " ": "properties not modified",
      "C": "properties conflicted",
      "M": "properties modified",
  }  
  return propertyDict[propertyChar]

def lockColDescription(lockChar):
  """converts the character from SVN into a meaningful message"""
  lockDict = {
      " ": "directory not locked",
      "L": "directory locked",
  }
  return lockDict[lockChar]

def getOutputOfSysCommand(commandText):
  p = subprocess.Popen(commandText, shell=True, bufsize=1024, stdout=subprocess.PIPE)
  p.wait()
  stdout = p.stdout
  return stdout.read()
  