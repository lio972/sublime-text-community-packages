#
# emacs-style killbuffer commands; kill, and yank
# 
import sublimeplugin, sublime, re

#
# An implementation of the emacs kill ring.
#
class KillRing:
  def __init__(self):
    # constructs the killring, a list acting basically 
    # as a stack. Items are added to it, and currently not removed.
    self.killRing = [""]
    # the last kill position remembers where the last kill happened; if
    # the user moves the cursor or changes buffer, then killing starts a 
    # new kill ring entry
    self.LastKillPosition = -1
    
  def peek(self):
    # returns the top of the kill ring; what will
    # be inserted on a basic yank.
    return self.killRing[-1]
    
  def new(self):
    # starts a new entry in the kill ring.
    self.killRing.append("")
    
    
  def append(self, content):
    # appends killed data to the current entry. 
    # Also updates the windows clipboard with 
    # everything in this kill entry
    self.killRing[-1] = self.killRing[-1] + content
    sublime.setClipboard(self.killRing[-1])
 
  def choices(self):
    # tuples of integers with kill-ring entries. 
    # Used by the yank choice command
    choiceArr = []
    for i in range(1,len(self.killRing)):
      choiceArr.append( (i,self.killRing[i]) )
    choiceArr.append( ("clipboard", "Windows Clipboard: " + sublime.getClipboard()))
    return choiceArr
    
  def get(self, idx):
    # gets a numbered entry in the kill ring
    return self.killRing[idx]

killRing = KillRing()

def expandSelectionForKill(view, begin, end):
  """Returns a selection that will be cut; basically, 
  the 'select what to kill next' command."""
  
  # the emacs kill-line command either cuts 
  # until the end of the current line, or if 
  # the cursor is already at the end of the 
  # line, will kill the EOL character. Will 
  # not do anything at EOF
  
  if  atEOL(view, end):
    # select the EOL char
    selection = sublime.Region(begin, end+1)
    return selection
    
  elif atEOF(view, end):
    # at the end of file, do nothing; the 
    # selection is just the initial selection
    return sublime.Region(begin, end)
    
  else:
    # mid-string -- extend to EOL
    current = end
    while not atEOF(view, current) and not atEOL(view, current):
      current = current+1
    selection = sublime.Region(begin,current)
    return selection

def atEOL(view, point):
  nextChar = view.substr(point)
  return  nextChar == "\n"

def atEOF(view, point):
  nextChar = view.substr(point)
  return ord(nextChar) == 0

  

#
# Kill Line
#
class EmacsKillLineCommand(sublimeplugin.TextCommand):
        
  def isEnabled(self, view, args):
    # disable kill for multi-selection. Too much of a headache!
    if len(view.sel()) != 1:
      return False
      
    # if we are at the end of the file, we can't kill.
    s = view.sel()[0]
    charAfterPoint = view.substr(s.end())
    if ord(charAfterPoint) == 0:
      # EOF
      return False
      
    return True

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
class EmacsYankChoiceCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    # choose from the yank-buffer using the quick panel
    global killRing
    choices = killRing.choices()
    names = [name for (idx, name) in choices]
    idx = ["%s" % idx for (idx, name) in choices]
    #print "YANK CHOICE IN " + view.fileName()
    view.window().showQuickPanel("", "emacsYank", idx, names)

#
# Yank the most recent kill, or 
# if an argument is specified, 
# that numbered kill ring entry
#
class EmacsYankCommand(sublimeplugin.WindowCommand):
 
  def run(self, window, args):
    global killRing
    
    valueToYank = killRing.peek()

    if len(args) == 0:
      # no arguments means the command 
      # is being called directly
      valueToYank = sublime.getClipboard()
    elif args[0] == "clipboard":
      # the user has chosen to yank windows clipboard.
      valueToYank = sublime.getClipboard()
    else:
      # an argument means it's been called from 
      # the EmacsYankChoiceCommand
      idx = int(args[0])
      valueToYank = killRing.get(idx)
    
    viewToInsert = window.activeView()
    
    # we no longer need the yankView, if it was set.
    yankView = None
    for s in viewToInsert.sel():
      viewToInsert.erase(s)
      viewToInsert.insert(s.begin(), valueToYank)
            
    # once we've yanked, we definitely don't want to
    # reuse the old kill buffer
    killRing.LastKillPosition = -1
    

