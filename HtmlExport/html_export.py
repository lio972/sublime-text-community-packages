#################################### IMPORTS ###################################

from __future__ import with_statement

from os.path import split, join, normpath, splitext

from plist import parse_plist

from build_css import camelizeString, getCSSFromThemeDict, getScopes

import sublime, sublimeplugin, cgi, re, webbrowser

################################### SETTINGS ###################################

OPEN_HTML_IN_EDITOR = 0

################################### TEMPLATES ##################################

HTML_TEMPLATE = """<html>
<head>
    <title> %s </title>
    <link rel="stylesheet" href="%s.css" type="text/css" charset="utf-8" />
    <style type='text/css'>
        body {margin:0; padding:0;}
        pre {padding: 1em; font: 12px "DejaVu Sans Mono", monospace;}
    </style>
</head>
<body>
%s
</body>
</html>
"""

################################### FUNCTIONS ##################################

def writeHTML(html, fn, theme):
    with open('%s.html' % fn, 'w') as fh:
        fh.write(HTML_TEMPLATE % (fn, camelizeString(theme), html))

def getThemeName(colorScheme):
    return splitext(split(colorScheme)[1])[0]

def getThemeAbsPath(colorScheme):
    appdataPath = split(sublime.packagesPath())[0]
    return normpath(join(appdataPath, colorScheme))

def getCssScopes(colorScheme):
    return getScopes(parse_plist(getThemeAbsPath(colorScheme)))

def writeCSS(colorScheme):
    theme = camelizeString(getThemeName(colorScheme))
    themePList = getThemeAbsPath(colorScheme)
    css = getCSSFromThemeDict(parse_plist(themePList))
    with open("%s.css" % theme, 'w') as fh:
        fh.write(css)
        
def getLineStartPts(view, start, end):
    pt, lines  = start, [start]
    while pt < end:
        pt = view.line(pt).end() + 1
        lines.append(pt)
    return lines

def getSelectionRange(view):
    sel = view.sel()[0]
    if not sel.empty():
        expanded = view.line(sel)
        return expanded.begin(), expanded.end()
    else:
        return 0, view.size()

################################################################################

def leveledScopes(scope):
    return [l.replace('.', ' ').split() for l in scope.split(' ') if l]

def selectorSpecificity(selector, scope):
    allSelectors = leveledScopes(selector)
    allScopes = leveledScopes(scope)

    start = []
    for selectors in allSelectors:
        for scopeLevel, scopes in enumerate(allScopes):
            if not [x for x in selectors if x not in scopes]:
                start.append((scopeLevel+1, len(selectors)))
            
    return start[-1:]

def getCssClassAtPt(pt, view, cssScopes):
    candidates = []
    syntaxAtPoint = " ".join(reversed(view.syntaxName(pt).split()))
    
    for cssClass, scopes in cssScopes.items():
        for scope in scopes:
            if view.matchSelector(pt, scope):
                specificity = selectorSpecificity(scope, syntaxAtPoint)
                candidates.append((specificity, cssClass))
                
    if candidates:
        return sorted(candidates)[-1][1]

################################### COMMANDS ###################################

class HtmlExportCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        tab = ' ' * view.options().get('tabSize')
        
        scopeCache = {}
        previousSyntax = ''
        previousCssClass = ''

        colorScheme = view.options().get('colorscheme')
        theme = getThemeName(colorScheme)
        cssScopes = getCssScopes(colorScheme)
        
        selRange = getSelectionRange(view)
        
        currentLineNumber = view.rowcol(selRange[0])[0]
        lineStartPts = getLineStartPts(view, *selRange)
        lnCols = `len(`view.rowcol(lineStartPts[-1]-1)[0]`)`
        lineNumbersTemplate= "<span class='lineNumber'>%"+ lnCols + "d  </span>"
        
        html = ["<pre class='%s'>" % camelizeString(theme)]
        for pt in xrange(*selRange):
            if pt in lineStartPts:
                currentLineNumber +=1
                html.append(lineNumbersTemplate % currentLineNumber)
                
            scopeAtPt = view.syntaxName(pt)            
            
            if scopeAtPt != previousSyntax:
                if scopeAtPt in scopeCache:
                    cssClassAtPt = scopeCache[scopeAtPt]
                else:                    
                    cssClassAtPt = getCssClassAtPt(pt, view, cssScopes)
                                    
                if previousCssClass != cssClassAtPt:
                    if previousCssClass: html.append("</span>")
                    
                    if cssClassAtPt: # in case class is None
                        html.append("<span class='%s'>" % cssClassAtPt)
                
                scopeCache[scopeAtPt] = cssClassAtPt
                previousSyntax = scopeAtPt
                previousCssClass = cssClassAtPt
                
            html.append(cgi.escape(view.substr(pt).replace('\t', tab)))
        
        html.append("</pre>")
        
        writeHTML("".join(html), view.fileName(), theme)
        writeCSS(colorScheme)
        
        htmlFile = "%s.html" % view.fileName()
        webbrowser.open(htmlFile)
        
        if OPEN_HTML_IN_EDITOR: view.window().openFile(htmlFile)