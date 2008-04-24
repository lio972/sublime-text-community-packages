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
        tabSize = view.options().get('tabSize')
        tab = tabSize * " "
        
        ### FIND THE $SELECTION DISPLACEMENT
        fn = normpath(join(split(sublime.packagesPath())[0], args[0]))        
        with open(fn) as fh:
            soup = BeautifulSoup(fh)
            snippet = soup.content.contents[0]

        for l in snippet.split("\n"):
            paramIndex = l.find("$SELECTION")
            if paramIndex != -1:
                paramMatch = re.search(r"\$.*?(\$SELECTION).?", l)
                if paramMatch: paramIndex = paramMatch.span()[0]
                
                spaces = 0
                for ch in l[:paramIndex]:
                    if ch == " ": spaces += 1
                    elif ch == "\t": spaces += tabSize
                break
            else:
                spaces = 0
            
        # SELECTION DISPLACEMENT
        for sel in view.sel():
            if sel.empty(): continue
            newsel = view.line(sel)
            start, end = newsel.begin(), newsel.end()
                                    
            selstr = view.substr(newsel).replace("\t", tab)
            selstr = stripPreceding( selstr,
                                     padding = spaces * " ",
                                     rstrip = False )            
            displacement = 0
            for i in xrange(start, end):
                if view.substr(i).isspace(): displacement += 1
                else: break
                
            modifiedRegion = sublime.Region(start+displacement, end)

            view.sel().subtract(sel)
            view.sel().add(modifiedRegion)
            view.replace(modifiedRegion, selstr)
        
        view.runCommand('insertSnippet', args)