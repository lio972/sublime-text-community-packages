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
    
    stripped = "\n".join(   [split[0][anchorPoint:]]      +\
                [padding + l[anchorPoint:] for l in split[1:]] )

    return  stripped.rstrip("\n") if rstrip else stripped
            
class RelativeIndentCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        if args[0] == 'paste':
            selection = sublime.getClipboard().replace("\r\n", "\n")
            selection = stripPreceding(selection, padding = '')
            view.runCommand('insertInlineSnippet', ['$PARAM1', selection])
        else:
            view.runCommand('expandSelectionTo line')
            view.runCommand(args[0])

def regionFirstNoPrecedingSpace(view, region, lines=True):
    region = view.line(region)
    start, end = region.begin(), region.end()
    displace = 0
    for x in xrange(start, end):
        if view.substr(x).isspace():
            displace += 1
        else: break
    
    start = start+displace
    if not lines: end = int(start)
    
    return sublime.Region(start, end)

def getTab(view):
    return view.options().get('tabSize') * " "

def substrStripPrecedingCommonSpace(view, region, padSecondary="    "):
    region = view.line(region)
    sel = view.substr(region).replace("\t", getTab(view))
    return stripPreceding(sel, padding = padSecondary)    

def eraseSelectionLines(view):
    numSel = len(view)
    for sel in view.sel(): 
        if not sel.empty(): view.erase(view.fullLine(sel))

class ParamPerSelectionSnippetCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        selections = []
        selSet = view.sel()
        sel1 = selSet[0]
        
        for sel in selSet:
            selections.append(substrStripPrecedingCommonSpace(view, sel))
        
        primarySelection = regionFirstNoPrecedingSpace(view, sel1)
        primaryStart = sublime.Region( primarySelection.begin(),
                                       primarySelection.begin() )
        
        selSet.subtract(sel1)
        selSet.add(primarySelection)
        eraseSelectionLines(view)
        selSet.clear()

        selSet.add(primaryStart)
        
        view.runCommand('insertSnippet', args + selections)

class RelativeIndentSnippetCommand(sublimeplugin.TextCommand):
    """ RelativeIndentSnippet: insert snippets maintaining indentation  """
    
    def run(self, view, args):
        for sel in view.sel():
            if sel.empty(): continue
            
            selectionStripped = substrStripPrecedingCommonSpace(view, sel)
            modifiedRegion = regionFirstNoPrecedingSpace(view, sel)
            
            view.sel().subtract(sel)
            view.sel().add(modifiedRegion)
            view.replace(modifiedRegion, selectionStripped)
        
        view.runCommand('insertSnippet', args)