#
# AutomaticBackupsPlugin.py
# (c) Steve Cooper, 2008
# This software comes with NO WARRANTIES. 
#
from __future__ import with_statement
import sublime, sublimeplugin, os, shutil, sys
from glob import fnmatch
from functools import partial

import backups

class NavigateBackupsCommand(sublimeplugin.TextCommand):
  index = None
  justReverted = False
  backupFiles = None

  def run(self, view, args):
    if self.index is None:
      f, ext = os.path.splitext(os.path.split(view.fileName())[1])        
      self.backupPath = backups.backupFilePath(view, just_dir=True)
      self.backupFiles = filter(lambda x: fnmatch.fnmatch(x, '%s*%s' % (f,ext)), 
                                os.listdir(self.backupPath))
      self.index = len(self.backupFiles)-1

    if args[0] == 'forward':
      self.index +=1 
      self.index = min(len(self.backupFiles)-1, self.index)
    else:
      self.index -=1 
      self.index = max(0, self.index)

    if self.backupFiles:
      if self.index == len(self.backupFiles)-1:
        if not self.justReverted:
          sublime.setTimeout(partial(view.runCommand, 'revert'), 50)
          self.justReverted = True
      else:
        backup = self.backupFiles[self.index]
        print backup
        if args[0] == 'backward': self.justReverted = False
        backup = os.path.join(self.backupPath, backup)
        with file(backup) as old_file:

          #view.replace scrolls around erratically.
          view.erase(sublime.Region(0, view.size()))
          view.insert(0, old_file.read())

  def onActivated(self, view):
    self.reInit()

  def onLoad(self, view):
    self.reInit()

  def onPostSave(self, view):
    self.reInit()

  def reInit(self):
    self.index = None
    self.justReverted = False

  def isEnabled(self, view, args):
    return True

class AutomaticBackupsPlugin(sublimeplugin.Plugin):  
  """Creates an automatic backup of every file you save. This
  gives you a rudimentary mechanism for making sure you don't lose
  information while working."""


  def onPostSave(self, view):
    """When a file is saved, put a copy of the file into the 
    backup directory"""

    buffer_file_name = view.fileName()
    newname = backups.backupFilePath(view)      

    if newname == None:
      return

    backup_dir, file_to_write = os.path.split(newname)

    # make sure that we have a directory to write into
    if (os.access(backup_dir, os.F_OK) == False):
      os.makedirs(backup_dir)

    backups.log("backing up to " + newname)
    shutil.copy(buffer_file_name, newname)