"""
Sublime Text - PowerUser Package
By: Eblin "EJ12N" Lopez (ej12n at yahoo dot com)
"""
#stuff for plugins :)
import sublime, sublimeplugin
import string, textwrap, re

#stuff for execSel command
import __builtin__, sys, os, calendar, datetime, random, time, cgi, urllib
from htmlentitydefs import name2codepoint as n2cp


"""
Save current buffer (tab) and exits sublime but preserves the session :)
"""
class saveAndExit(sublimeplugin.TextCommand):
  def run(self, view, args):
    window = view.window();
    window.runCommand('save')
    window.runCommand('hotExit')

"""
Copies Scope to Clipboard
---
Useful for when you are creating snippets or macros and you want to assign it
to a certain scope only. By default Sublime Text only allows you to see
the current scope, so you have to memorize it and then write it. That's gone with
this command :) 
""" 
class ScopeToClipboardCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    sublime.setClipboard(view.syntaxName(view.sel()[0].begin()).strip());
    sublime.statusMessage('Scope copied to clipboard')
    
class ReverseStringCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      sublime.statusMessage('reversing strings!')
      s = view.substr(region)
      s = s[::-1]
      view.replace(region, s)

class ReverseSelectionDirections(sublimeplugin.TextCommand):
  def run(self, view, args):
    sels = [sublime.Region(sel.b, sel.a) for sel in view.sel()]
    view.sel().clear()
    map(view.sel().add, sels)

class OpenFileUnderCursorCommand(sublimeplugin.WindowCommand):
  def run(self, window, args):
    curdir = os.getcwdu()
    view = window.activeView()
    for region in view.sel():
      s = view.substr(region)
      if(s != ''):
        f = curdir + '\\' + s
        
        if(os.path.exists(f)):
          window.openFile(f)
        else:
          sublime.errorMessage('The file under cursor does not exists in the directory of the current file')
      else:
        # f = curdir + '\\' + str(args[1])
        word_under_cursor = view.substr(view.word(view.sel()[0].begin()))
        dot_pos = view.find('\.',view.sel()[0].begin())
        if(dot_pos):
          f = view.substr(view.word(dot_pos))
          
      if(os.path.exists(f)):
        window.openFile(f)
      else:
        sublime.errorMessage('The file under cursor does not exists in the directory of the current file')

"""
Nick (sublimator) functions :)
Thank you very much Nick!
"""

class DeleteLineCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    print 'hello world'
    for sel in view.sel():
      view.erase(view.fullLine(sel))

class ReloadProjectCommand(sublimeplugin.WindowCommand):
  def isEnabled(self, window, args):
    return window.project()

  def run(self, window, args):
    project = window.project().fileName()
    window.runCommand('closeProject')
    window.runCommand('openProject', [project.replace('\\','/')])

class StripTrailingOnSaveCommand(sublimeplugin.TextCommand):

  def strip_trailing(view, save_recent_indentation=True, ignore='string'):
    trailing_spaces = view.findAll('[ \t]+(?![^\n])')
    if not trailing_spaces: return

    if save_recent_indentation:
      for sel in view.sel():
        if not sel.empty(): continue
        line = view.line(sel)
  
        if view.substr(line).isspace() and sel.end() == line.end():
          pos = bisect.bisect(trailing_spaces, line) - 1
          trailing_sel = trailing_spaces[pos]

          if line.contains(trailing_sel):
            del trailing_spaces[pos]

    for sel in reversed(trailing_spaces):
      if ignore:
        pt_range = xrange(sel.begin(), sel.end())
  
        if any(view.matchSelector(pt, ignore) for pt in pt_range):
          continue

      view.erase(sel)

  def onPreSave(self, view):
    self.strip_trailing(view)
  
  def run(self, view, args):
    self.strip_trailing(view, ignore=None, save_recent_indentation=False)

"""
DO MULTIPLE SELECTION - MULTIPLE SELECTIONS WITHOUT USING MOUSE!
Allows you to do multiple selections without using the mouse.
Usage: Just navigate to where you want to add a new selection
      Run the command (via shortcut I suppose) and then just run the command to
      restore your selections :D
"""
class DoMultipleSelectionCommand(sublimeplugin.TextCommand):
  selections = [] #  Store selections here

  def run(self, view, (args, )):
    if args == 'store':
      # Store the selections
      self.selections.extend(list(view.sel()))
      sublime.statusMessage("Selection stored sucessfully.")
    else:
      # Restore the selections
      while self.selections:
        view.sel().add(self.selections.pop())
      sublime.statusMessage("All Selection have been restored.")

"""
/END Nick functions
"""

"""
Duplicates Current Line or Selected text
---
Duplicates current line if there's nothing selected. Else duplicates content
"""
class DuplicateLineCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if region.empty():
        line = view.line(region)
        lineContents = view.substr(line) + '\n'
        view.insert(line.begin(), lineContents)
      else:
        s = view.substr(region)
        view.insert(region.end(), s)

"""
HTML Entities
---
It converts selected text to HTML entities, just like textmate does...
"""
class UndoEntitiesCommand(sublimeplugin.TextCommand):
  def run(self, view, args):

    def decode_htmlentities(string):
      def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
          # decoding by number
          if match.group(2) == '':
              # number is in decimal
              return unichr(int(ent))
          elif match.group(2) == 'x':
              # number is in hex
              return unichr(int('0x'+ent, 16))
        else:
          # they were using a name
          cp = n2cp.get(ent)
          if cp: return unichr(cp)
          else: return match.group()
  
        entity_re = re.compile(r'&(#?)(x?)(\w+);')
        return entity_re.subn(substitute_entity, string)[0]
  
    for region in view.sel():
      # line = view.line(region)
      s = view.substr(region)
      view.replace(region, decode_htmlentities(s))

class DoEntitiesCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      s = view.substr(region)
      view.replace(region, cgi.escape(s, 1))

"""
HTML URL Escaping
---
URL Escapes selected text, just like textmate does...
"""
class DoURLEscapeCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      s = view.substr(region)
      view.replace(region, urllib.quote(s))

class UndoURLEscapeCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      s = view.substr(region)
      view.replace(region, urllib.unquote(s))

"""
Add Numbers in selected text.
"""
class AddNumbersCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if not region.empty():
        # Get the selected text
        line = view.line(region)
        s = view.substr(region)

        num = re.compile('([0-9]+(\.[0-9]+)?)')
        isNum = num.finditer(s)
        totalNum = 0;

        # sublime.statusMessage(m.group(2))

        for m in isNum:
          if m.group(2):
            totalNum = float(totalNum) + float(m.group())
          else:
            totalNum = int(totalNum) + int(m.group())

        view.insert(line.end(), '\n= ' + str(totalNum))

"""
Firebug like Number increasing/decreasing.
---
Ever used firebug? Ever use up/down arrows to increase/decrease a number?
Well this is what that does ;)
"""
class UpNumCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if not region.empty():
        # Get the selected text
        s = view.substr(region)

        # Put it on the status bar?
        num = re.compile('([0-9]+)([a-zA-Z%]+)?')
        isNum = num.match(s)
        if (isNum):
          upNum = int(isNum.group(1)) + 1
          # sublime.statusMessage(isNum.group())
          # Replace the selection with transformed text
          if(isNum.group(2)):
            view.replace(region, str(upNum) + isNum.group(2))
          else:
            view.replace(region, str(upNum))

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion()

class DownNumCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if not region.empty():
        # Get the selected text
        s = view.substr(region)

        # Put it on the status bar?
        num = re.compile('([0-9]+)([a-zA-Z%]+)?')
        isNum = num.match(s)
        if (isNum):
          downNum = int(isNum.group(1)) - 1
          # sublime.statusMessage(str(upNum))
          # Replace the selection with transformed text
          if(isNum.group(2)):
            view.replace(region, str(downNum) + isNum.group(2))
          else:
            view.replace(region, str(downNum))

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion()

class UpNumTenCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if not region.empty():
        # Get the selected text
        s = view.substr(region)

        # Put it on the status bar?
        num = re.compile('([0-9]+)([a-zA-Z%]+)?')
        isNum = num.match(s)
        if (isNum):
          upNum = int(isNum.group(1)) + 10
          # sublime.statusMessage(isNum.group())
          # Replace the selection with transformed text
          if(isNum.group(2)):
            view.replace(region, str(upNum) + isNum.group(2))
          else:
            view.replace(region, str(upNum))

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion()

class DownNumTenCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if not region.empty():
        # Get the selected text
        s = view.substr(region)

        # Put it on the status bar?
        num = re.compile('([0-9]+)([a-zA-Z%]+)?')
        isNum = num.match(s)
        if (isNum):
          downNum = int(isNum.group(1)) - 10
          # sublime.statusMessage(str(upNum))
          # Replace the selection with transformed text
          if(isNum.group(2)):
            view.replace(region, str(downNum) + isNum.group(2))
          else:
            view.replace(region, str(downNum))

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion()

"""
Execute Selected Text
---
This evals selected text and puts result of that in new line.
This gives you power to execute anything in python and use it on your editor!
Ex:
Selected Text: 5+5
Output: 10 (in a new line)
"""
class ExecSelCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if not region.empty():
        # Get the selected text
        line = view.line(region)
        s = view.substr(region)

        evalResult = eval(s, globals(), locals())

        view.insert(line.end(), '\n' + str(evalResult))

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion()

"""
Execute Selected Text & Replace
---
This evals selected text and replaces the selection with the result.
This gives you power to execute anything in python and use it on your editor!
Ex:
Selected Text: 5+5
Output: 10 (replacing selection)
"""
class ExecSelReplaceCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if not region.empty():
        # Get the selected text
        line = view.line(region)
        s = view.substr(region)

        evalResult = eval(s, globals(), locals())

        view.replace(region, str(evalResult))

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion()

"""
Put Command -- Put X times "my string"
---
You can use it with the SublimeRunCmd and then you can do
put 5 times "hello world\n"
you get:
hello world
hello world
hello world
hello world
hello world

Try it!
"""
class PutCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    # args = string.join(args,'')
    # sublime.statusMessage(str(args[1]))
    num = re.compile('([0-9]+)')
    isNum = num.match(args[0])
    if(isNum and args[1] == 'times' ):
      # sublime.statusMessage(str(args[2]))
      # view.runCommand('insertAndDecodeCharacters "' + str(args) + '"')
      view.runCommand('times ' + str(isNum.group(1)) + ' insertAndDecodeCharacters "' + str(args[2]) + '"')

"""
SublimeRunCmd - Shorcut for view.runCommand
---
This is so you can type and execute commands in the editor, without having to
go to the output panel. Just use a shortcut :D
"""
class SublimeRunCmdCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    for region in view.sel():
      if not region.empty():
        s = view.substr(region)
        evalResult = view.runCommand(s)

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion()

"""
Title Case Command
"""
def transformSelectionText(f, v):
  for s in v.sel():
    if not s.empty():
      txt = f(v.substr(s))
      v.replace(s, txt)

class TitleCaseCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
    transformSelectionText(string.capwords, view)

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion()

#====================================================================================================================================================================================================
"""
ALL THE FOLLOWING WERE TAKEN FROM COMMUNITY PACKAGES.
THEY ARE HERE BECAUSE I USE THEM AND INSTEAD OF DOWNLOADING A BUNCH OF PACKAGES
I CAN JUST USE THIS ONE :) -- VERY CONVINIENT WHEN YOU WORK IN MORE THAN 1 PC.
"""

"""
Excellent plugins by gpfsmurf
"""
#PasteColumn
class pasteColumnCommand(sublimeplugin.TextCommand):
  """
  Use this command to cut and paste whole columns.
   
  If you had i.e. 10 selection cursors when cutting the column, you need 10
  selection cursors to paste the column.
  """
  def run(self, view, args):
    clip = sublime.getClipboard().split(u"\n")
    for region in view.sel():
      view.replace(region, clip.pop(0))

  def isEnabled(self, view, args):
    return sublime.getClipboard() != ""

#Strip Selection
class stripSelectionCommand(sublimeplugin.TextCommand):
  """
  Removes leading and trailing whitespace from selections
  """
  def run(self, view, args):
    rs = []
    for region in view.sel():
      s = view.substr(region)
      if(not s.strip()):
        # strip whitespace selections
        rs.append(sublime.Region(region.begin(),region.begin()))
        continue
      a, b = region.a, region.b
      if(b > a):
        a += len(s) - len(s.lstrip())
        b -= len(s) - len(s.rstrip())
      else: # selection is inverted, keep it that way
        b += len(s) - len(s.lstrip())
        a -= len(s) - len(s.rstrip())
      rs.append(sublime.Region(a,b))
    view.sel().clear()
    for region in rs:
      view.sel().add(region)

  def isEnabled(self, view, args):
    return view.hasNonEmptySelectionRegion();

"""
For more info see:
http://www.sublimetext.com/forum/viewtopic.php?f=5&t=158#p843
By: eric1235711
"""
class RightEraseByCharClassCommand(sublimeplugin.TextCommand):
    def run(self, view, args):

      # patterns
      pt_s = re.compile(r"\s")
      pt_w = re.compile(r"\w")
      pt_o = re.compile(r"[^\w\s]")

      sz = view.size()

      for region in view.sel():
         pos = region.begin()

         # check first char
         if pt_w.match(view.substr(pos)) :
            pt = pt_w
         elif pt_s.match(view.substr(pos)) :
            pt = pt_s
         else :
            pt = pt_o

         # removes according to first char
         while pt.match(view.substr(pos)) and pos < sz :
            view.erase(sublime.Region(pos,pos+1))

class LeftEraseByCharClassCommand(sublimeplugin.TextCommand):
   def run(self, view, args):

      # patterns
      pt_s = re.compile(r"\s")
      pt_w = re.compile(r"\w")
      pt_o = re.compile(r"[^\w\s]")

      for region in view.sel():
         pos = region.end()-1

         # check last char
         if pt_w.match(view.substr(pos)) :
            pt = pt_w
         elif pt_s.match(view.substr(pos)) :
            pt = pt_s
         else :
            pt = pt_o

         # removes according to last char
         while pos > 1 and pt.match(view.substr(pos)) :
            view.erase(sublime.Region(pos,pos+1))
            pos -= 1

"""
These 2 do the same as above but they just take away 1 character...
For more info about these functions visit:
http://www.sublimetext.com/forum/viewtopic.php?p=1772#p1772
"""
class SingleRightEraseByCharClassCommand(sublimeplugin.TextCommand):
  def run(self, view, args):
  
    # patterns
    pt_s = re.compile(r"\s")
    pt_w = re.compile(r"\w")
    pt_o = re.compile(r"[^\w\s]")
  
    sz = view.size()
  
    for region in view.sel():
       pos = region.begin()
  
       # check first char
       if pt_w.match(view.substr(pos)) :
          pt = pt_w
       elif pt_s.match(view.substr(pos)) :
          pt = pt_s
       else :
          pt = pt_o
  
       # removes according to first char
       if pt.match(view.substr(pos)) and pos < sz :
          view.erase(sublime.Region(pos,pos+1))

class SingleLeftEraseByCharClassCommand(sublimeplugin.TextCommand):
   def run(self, view, args):
    # patterns
    pt_s = re.compile(r"\s")
    pt_w = re.compile(r"\w")
    pt_o = re.compile(r"[^\w\s]")

    for region in view.sel():
      pos = region.end()-1
      # check last char
      if pt_w.match(view.substr(pos)) :
         pt = pt_w
      elif pt_s.match(view.substr(pos)) :
         pt = pt_s
      else :
         pt = pt_o

      # removes according to last char
      if pos > 1 and pt.match(view.substr(pos)):
       view.erase(sublime.Region(pos,pos+1))
       pos -= 1