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
        fn = normpath(join(split(sublime.packagesPath())[0], args[0]))        
        with open(fn) as fh:
            soup = BeautifulSoup(fh)
            snippet = soup.content.contents[0]
        
        SELECTION = "$SELECTION"
        
        paramIndex = None
        for l in [l for l in snippet.split("\n") if SELECTION  in l]:
            paramMatch = re.search(r"\$.*?(\%s).?" % SELECTION , l)
            if paramMatch:
                paramIndex = paramMatch.span()[0]
                break
            else:
                paramIndex = l.find(SELECTION)
                if paramIndex == -1: paramIndex == None
                else: break

        if paramIndex is None: return

        tab = view.options().get('tabSize') * " "

        # Expand Selection to line
        for i, sel in enumerate(view.sel()):
            if sel.empty(): continue
            newsel = view.line(sel)
            view.sel().subtract(sel)
            view.sel().add(newsel)
        
        # Insert at the right point
        # TODO: do this by altering regions
        
        if not view.sel()[0].empty():
            view.runCommand("moveTo bol extend")
        
        # Strip out preceding characters if any      
        for sel in view.sel():
            if sel.empty(): continue
            selstr = view.substr(sel).replace("\t", tab)
            
            selstr = stripPreceding(selstr,
                                    padding = paramIndex * " ", 
                                    rstrip = False )
            view.replace(sel, selstr)

        # Insert the snippet
        view.runCommand('insertSnippet', args)