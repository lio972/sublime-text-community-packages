#HYPERLINKING
#
# A Plugin for Sublime Text, By Steve Cooper
#
# see README.txt for usage instructions.

import sublime, sublimeplugin, re, os

class NavigateBase(sublimeplugin.TextCommand):
  def ensureFile(self, fileName):
    if os.path.exists(fileName) == False:
      print "creating %s" % fileName
      f = open(fileName, 'w')
      f.write("")
      f.close()

  def run(self, view, args):
    print "base class!"

class NavigateToWikiIndexPageCommand(NavigateBase):
  """This command creates a new view containing all the files 
  which can be visited from the currently-visible wiki file 
  """

  def run(self, view, args):
    dirName = os.path.dirname(view.fileName())
    indexFileName = os.path.join(dirName, "IndexPage.wiki")
    self.ensureFile(indexFileName)
    
    allFiles = os.listdir(dirName)
    wikiFiles = [ "[%s]" % f[:-5] for f in allFiles if os.path.isfile(f) and f.lower().endswith(".wiki")]
    wikiFiles.sort()
    bufferContent = "FILES IN " + dirName + "\r\n\r\n" + "\r\n".join( wikiFiles )
    newView = view.window().openFile(indexFileName)
    # openFile() is asynchronous, so it returns None. Therefore we can't insertfil
    #newView.insert(0, bufferContent)

  def isEnabled(self, view, args):
    return view.fileName()
    
class NavigateToWikiPageCommand(NavigateBase):
  """This command takes the user to a wiki page under the cursor. 
  Eg, if the cursor is in NewPa|geToNavigateTo, and the user executes
  the command, NewPageToNavigateTo.wiki in the same folder will be opened
  """  
  
  # OLD FORM
  # matches, eg, ExampleWikiFile, MissingFile
  #wikiWordPattern = r"^([A-Z][a-z0-9]+){2,}"
  
  # NEW FORM
  # matches any word
  wikiWordPattern = r"^\w+\b"
  
  # what extension do wiki pages have?
  wikiFileExtension = "wiki"
  
  def run(self, view, args):
    # get the wikiname under the cursor.
    for s in view.sel():
      # try to find a phrase in square brackets
      name = self.phraseInSquareBrackets(view, s)
      if name == None:
        # nothing in square brackets -- try a word
        name = self.wordUnderCursor(view, s)
      if name == None:
        # total failure!
        sublime.statusMessage("No suitable hyperlink found. Try square brackets around the text.")
        return
      
      candidateFileName = os.path.split(view.fileName())[0] + "\\" + name + "." + self.wikiFileExtension
      print candidateFileName
      if (os.access(candidateFileName, os.R_OK)):
        sublime.statusMessage("Opening page: %s" % candidateFileName)
        view.window().openFile(candidateFileName)
      else:
      	if sublime.questionBox("Do you want to create %s" % candidateFileName):
          self.ensureFile(candidateFileName)
          sublime.statusMessage("No page at %s: starting new file" % candidateFileName)
          view.window().openFile(candidateFileName)
        
  def phraseInSquareBrackets(self, view, s):
    start = self.findStartSquareBracket(view, s)
    end = self.findEndSquareBracket(view, s)
    if end > 0:
      return view.substr(sublime.Region(start, end))
  
  def wordUnderCursor(self, view, s):
    wb = self.findWordBoundary(view, s)
    # see if what follows the word boundary is a wikiword
    word = self.getWordAtPoint(view, wb)
    return word
    
  def findEndSquareBracket(self, view, s):
    pos = s.begin()
    while True:
      if (pos == view.size()): return 0 # no end sq
      
      charAfterPoint = view.substr(sublime.Region(pos, pos+1))
      if charAfterPoint == "]":
        return pos
      if charAfterPoint == "[":
        return 0
      pos = pos + 1
    
  def findStartSquareBracket(self, view, s):
    pos = s.begin()
    while True:
      if (pos == 0): return 0
  
      #search for open square bracket before cursor
      charBeforePoint = view.substr(sublime.Region(pos-1, pos))
      if charBeforePoint == "[":
        return pos
      if charBeforePoint == "]":
        return 0
      pos = pos - 1  
  	
  def findWordBoundary(self, view, s):
    pos = s.begin()
    wbRx = re.compile(r"[^\w]\w")
    while True:
      if (pos == 0): return 0
  
      #search for not-word, word around cursor
      twoCharsAroundPoint= view.substr(sublime.Region(pos-1, pos+1))
      match = wbRx.match(twoCharsAroundPoint)
      if match:
        return pos
      pos = pos - 1
    
    
  def getWordAtPoint(self, view, p):
    wikiWordRx = re.compile(self.wikiWordPattern)
    stringToSearch = view.substr(sublime.Region(p, p+128))
    match = wikiWordRx.match(stringToSearch)
    if (match):
      return match.group(0)
    return None