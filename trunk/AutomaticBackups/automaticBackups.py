#
# AutomaticBackupsPlugin.py
# (c) Steve Cooper, 2008
# This software comes with NO WARRANTIES. 
#
from __future__ import with_statement
import sublime, sublimeplugin, os, shutil, sys
from glob import fnmatch
from functools import partial
from subprocess import Popen

import backups

WINMERGE = '"C:\Program Files\WinMerge\WinMergeU.exe"'

class NavigateBackupsCommand(sublimeplugin.TextCommand):  
  def __init__(self):
    self.reInit()
  
  def reInit(self):
    self.index = None
    self.justReverted = False
    self.foundBackupFiles = None
    self.currentFile = None
  
  def run(self, view, args):
    if self.index is None: self.findBackups(view)
      
    cmd = args[0]
    if cmd == 'forward': self.navForwards() 
    elif cmd == 'backward': self.navBackwards()
      
    if self.foundBackupFiles:
      if self.navigatedToEndOfBackups():
        if cmd != 'merge' and not self.justReverted:
          self.revert(view)
                   
      else:
        self.backup = self.foundBackupFiles[self.index]
        self.backupFullPath = os.path.join(self.backupPath, self.backup)
    
        if cmd == 'merge': self.merge()
        else: self.buffer(view)
  
  def navForwards(self):
    self.index +=1 
    self.index = min(len(self.foundBackupFiles)-1, self.index)
  
  def navBackwards(self):
    self.index -=1 
    self.index = max(0, self.index)
    self.justReverted = False

  def findBackups(self, view):
    fn = view.fileName()
    self.currentFile = fn

    f, ext = os.path.splitext(os.path.split(fn)[1])        
    self.backupPath = backups.backupFilePath(view, just_dir=True)
    
    dirListing = os.listdir(self.backupPath)
    
    self.foundBackupFiles = \
        filter(lambda x: fnmatch.fnmatch(x, '%s*%s' % (f,ext)), dirListing)

    self.index = len(self.foundBackupFiles)-1
  
  def merge(self):
    CMD = '%s /e /wr /s /x /ul /ur /dr "AUTOMATIC BACKUP: %s" "%s" "%s"' %\
           (WINMERGE, self.backup, self.currentFile, self.backupFullPath)

    Popen(CMD)

  def buffer(self, view):
    with file(self.backupFullPath) as old_file:
      view.erase(sublime.Region(0, view.size()))
      view.insert(0, unicode(old_file.read(), 'utf8'))

    sublime.statusMessage("%s [%s of %s]" %\
        (self.backup, self.index+1, len(self.foundBackupFiles)-1))
    
  def navigatedToEndOfBackups(self):
    return self.index == len(self.foundBackupFiles)-1

  def revert(self, view):
    sublime.setTimeout(partial(view.runCommand, 'revert'), 50)
    self.justReverted = True
    
  def onActivated(self, view):
    if view.fileName() != self.currentFile:
      self.reInit()

  def onLoad(self, view):
    self.reInit()

  def onPostSave(self, view):
    self.reInit()

  def isEnabled(self, view, args):
    return view.fileName()

class AutomaticBackupsPlugin(sublimeplugin.Plugin):  
  """Creates an automatic backup of every file you save. This
  gives you a rudimentary mechanism for making sure you don't lose
  information while working."""

  def onPostSave(self, view):
    """When a file is saved, put a copy of the file into the 
    backup directory"""

    buffer_file_name = view.fileName()
    
    # if buffer_file_name.endswith('.lnk'): return
    newname = backups.backupFilePath(view)      
    if newname == None:
      return

    backup_dir, file_to_write = os.path.split(newname)

    # make sure that we have a directory to write into
    if (os.access(backup_dir, os.F_OK) == False):
      os.makedirs(backup_dir)

    backups.log("backing up to " + newname)
    shutil.copy(buffer_file_name, newname)