from __future__ import with_statement

import sublime, sublimeplugin, re, os
from BeautifulSoup import BeautifulSoup
from os.path import join, split, normpath

def stripPreceding(selection, padding="", rstrip=True):
    spacesList = []
    spaces = 0
    
    split = selection.split("\n")
    for l in split:
        for ch in l:
            if ch == '\t' or ch == ' ': spaces += 1
            else:
                spacesList.append(spaces)
                spaces = 0
                break
                                       
    try: anchorPoint = min(spacesList)
    except ValueError: anchorPoint = 0
    
    stripped =  [split[0][anchorPoint:]] +\
                [padding + l[anchorPoint:] for l in split[1:]]
    
    stripped = "\n".join(stripped)
    
    return  stripped.rstrip("\n") if rstrip else stripped
                
class RelativeIndentPasteCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        selection = sublime.getClipboard().replace("\r\n", "\n")
        selection = stripPreceding(selection, padding = '')
                        
        view.runCommand('insertInlineSnippet', ['$PARAM1', selection])
        
class RelativeIndentCopyCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        view.runCommand('expandSelectionTo line')
        view.runCommand('copy')

class RelativeIndentSnippetCommand(sublimeplugin.TextCommand):
    """ RelativeIndentSnippet: insert snippets maintaining indentation  """
    
    def run(self, view, args):
        newsel = view.line(view.sel()[0])
        view.sel().clear()
        view.sel().add(newsel)
        
        selection = view.substr(newsel)
        if selection.strip():
            view.runCommand("moveTo bol extend")
        
        fn = normpath(join(split(sublime.packagesPath())[0], args[0]))
        
        PARAM = "$PARAM%s" % len(args)
        
        with open(fn) as fh:
            soup = BeautifulSoup(fh)
            snippet = soup.content.contents[0]
            snippet = snippet.replace("$SELECTION", PARAM)
        
        snippet = snippet.replace("\t", view.options().get('tabSize') * " ")
        
        paramIndex = None
        for l in [l for l in snippet.split("\n") if PARAM in l]:
            paramMatch = re.search(r"\$.*?(\%s).?" % PARAM , l)
            if paramMatch:
                paramIndex = paramMatch.span()[0]
                break
            else:
                paramIndex = l.find(PARAM)
                if paramIndex == -1: paramIndex == None
                else: break

        if paramIndex is None: return
        
        selection = stripPreceding( selection, 
                                    padding = paramIndex * " ", 
                                    rstrip = False )
                
        view.runCommand('insertInlineSnippet', [snippet] + args[1:] + [selection])
        
        # Get view.substr( of line() region of the first selection 
        # Strip preceding characters
        # Find the index of the $PARAM1 command
        # Pad the rest of the selection with that much 