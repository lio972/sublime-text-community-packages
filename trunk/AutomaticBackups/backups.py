#
# backups.py
# (c) Steve Cooper 2008
#
# Utilities for manipulating a backup store

import sublime, sublimeplugin, os, _winreg, re, datetime

def base_dir(view):
  options = view.options()
  backupDir = sublime.options().getString("backupDir")
  if (backupDir is None):
    #log("no backup dir specified")
    # change this if you want backups to go somewhere else
    return os.path.join(get_shell_folder("Personal"), "Sublime Text Backups")
  else:
    return backupDir

def log(message):
  print "Automatic backup: " + message


def timestampFile(file_name):
  """Puts a datestamp in file_name, just before the extension."""
  now = datetime.datetime.today()
  filepart, extensionpart = os.path.splitext(file_name)
  return "%s-%04d-%02d-%02d-%02d-%02d-%02d%s" % \
         (filepart, now.year, now.month, now.day, now.hour, now.minute, now.second, extensionpart) 


def backupFilePath(view, just_dir=False):
  """Creates a new name for the file to back up, 
  in the base directory, with a timestamp. 
  Eg, turns c:\\myfile.txt into d:\\backups\\c-drive\\myfile-2008-03-20-12-44-03.txt
  """
  buffer_file_name = view.fileName()
  backup_base = base_dir(view)
  unc_rx = re.compile('^\\\\\\\\') # unc format, eg \\svr\share
  drive_rx = re.compile('^[A-Za-z]\:\\\\') # drive-colon, eg c:\foo

  drive_match = drive_rx.match(buffer_file_name)
  unc_match = unc_rx.match(buffer_file_name)

  rewritten_path = None    

  if just_dir: buffer_file_name = os.path.split(buffer_file_name)[0]

  if (drive_match):
    # rewrite C:\foo\baras d:\backups\c-drive\foo\bar
    rewritten_path = os.path.join(backup_base, buffer_file_name[0] + "-drive", buffer_file_name[3:])
  elif (unc_match):
    # rewrite \\unc\share as d:\backups\network\unc\share
    rewritten_path = os.path.join(backup_base, "network", buffer_file_name[2:])

  if rewritten_path:
    return timestampFile(rewritten_path) if not just_dir else rewritten_path
  else:
    return None # we can't save this kind of file -- what the hell is it?


#
# FUNCTIONS FOR ACCESSING WINDOWS REGISTRY FOR USER'S SHELL FOLDERS
#  
def _substenv(m):
  return os.environ.get(m.group(1), m.group(0))

def get_shell_folder(name):
  """Returns the shell folder with the given name, eg "AppData", "Personal", 
    "Programs". Environment variables in values of type REG_EXPAND_SZ are expanded
    if possible."""

  HKCU = _winreg.HKEY_CURRENT_USER
  USER_SHELL_FOLDERS = \
                     r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
  key = _winreg.OpenKey(HKCU, USER_SHELL_FOLDERS)
  ret = _winreg.QueryValueEx(key, name)
  key.Close()
  if ret[1] == _winreg.REG_EXPAND_SZ and '%' in ret[0]:
    return re.compile(r'%([^|<>=^%]+)%').sub(_substenv, ret[0])
  else:
    return ret[0]
