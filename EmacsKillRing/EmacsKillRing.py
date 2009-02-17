#
# emacs-style killbuffer commands; kill, and yank
# 
import sublimeplugin, sublime, win32clipboard as w, win32con, re, unicodedata

#
# An implementation of the emacs kill ring.
#
class KillRing:
  def __init__(self):
    self.killRing = [""]
    self.LastKillPosition = -1
    
  def peek(self):
    return self.killRing[-1]
    
  def new(self):
    self.killRing.append("")
    
  def append(self, content):
    self.killRing[-1] = self.killRing[-1] + content
 
  def choices(self):
    choiceArr = []
    for i in range(0,len(self.killRing)):
      choiceArr.append( (i,self.killRing[i]) )
    return choiceArr
    
  def get(self, idx):
    return self.killRing[idx]

killRing = KillRing()


#
# Clipboard commands.
#
def getText(): 
    w.OpenClipboard() 
    d=w.GetClipboardData(win32con.CF_TEXT) 
    w.CloseClipboard() 
    return d 
 
def setText(aType,aString): 
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(aType,aString) 
    w.CloseClipboard()

def expandSelectionForKill(view, begin, end):
  nextChar = view.substr(end)
  endOfLine = nextChar == "\n"
  endOfFile = ord(nextChar) == 0
  if endOfLine:
    # select the EOL char
    selection = sublime.Region(begin, end+1)
    return selection
  elif endOfFile:
    # do nothing; the selection is just the initial selection
    return sublime.Region(begin, end)
  else:
    # mid-string -- extend to EOL
    current = end
    nextChar = view.substr(current)
    while nextChar != "\n":
      current = current+1
      nextChar = view.substr(current)
    selection = sublime.Region(begin,current)
    return selection

#
# Kill Line
#
class EmacsKillLineCommand(sublimeplugin.TextCommand):
        
  def isEnabled(self, view, args):
    # disable kill for multi-selection. Too much of a headache!
    return len(view.sel()) == 1

  def run(self, view, args):
    global killRing

    s = view.sel()[0]
    
    if killRing.LastKillPosition != s.begin() or killRing.LastKillPosition != s.end():
      # we've moved the cursor, meaning we can't 
      # continue to use the same kill buffer
      killRing.new()
      
    expanded = expandSelectionForKill(view, s.begin(), s.end())
    killRing.LastKillPosition = expanded.begin()
    killRing.append(view.substr(expanded))
    view.erase(expanded)
    
#
# Yank any clip from the kill ring
# 
class EmacsYankChoice(sublimeplugin.TextCommand):
  def run(self, view, args):
    # choose from the yank-buffer using the quick panel
    global killRing
    choices = killRing.choices()
    names = [name for (idx, name) in choices]
    idx = ["%s" % idx for (idx, name) in choices]
    print names
    print idx
    view.window().showQuickPanel("", "emacsYank", idx, names)

#
# Yank the most recent kill
#
class EmacsYank(sublimeplugin.TextCommand):
  def _init__(self):
    pass
  
  def run(self, view, args):
    global killRing
    if len(args) == 0:
      valueToYank = killRing.peek()
    else:
      idx = int(args[0])
      valueToYank = killRing.get(idx)
      
    print "YANKING '%s'" % valueToYank
    for s in view.sel():
      # yank the killBuffer here.  
      view.erase(s)
      view.insert(s.begin(), valueToYank)
      
    # once we've yanked, we definitely don't want to
    # reuse the old kill buffer
    killRing.LastKillPosition = -1
    
    