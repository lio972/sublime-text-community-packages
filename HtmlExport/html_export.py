#################################### IMPORTS ###################################

from __future__ import with_statement

from os.path import split, join, normpath, splitext

from scopes import Selector

import sublime, sublimeplugin, cgi, re, webbrowser

import plist, build_css

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
        fh.write(HTML_TEMPLATE % (fn, theme, html))

def getTheme(colorScheme):
    return splitext(split(colorScheme)[1])[0]

def getThemeAbsPath(colorScheme):
    appdataPath = split(sublime.packagesPath())[0]
    return normpath(join(appdataPath, colorScheme))

def getCssScopes(colorScheme):
    return build_css.getScopes (
        plist.parse_plist( getThemeAbsPath(colorScheme) )
    )

def writeCSS(colorScheme):
    theme = getTheme(colorScheme)
    themePList = getThemeAbsPath(colorScheme)
    css = build_css.getCSSFromThemeDict(plist.parse_plist(themePList))
    with open("%s.css" % theme, 'w') as fh:
        fh.write(re.sub(r"\.py\b", '.python', css))    
        
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

def getCssClassAtPt(pt, view, CssScopes):
    candidates = []
    for cssClass, scopes in CssScopes.items():
        for scope in scopes:
            if view.matchSelector(pt, scope):
                candidates.append((scope, cssClass))
    
    if candidates:
        leader = candidates.pop()
        while candidates:
            leaderScope, _ = leader
            candidateScope, candidateClass = candidates.pop()
            
            if Selector(candidateScope) > Selector(leaderScope):
                leader = candidateScope, candidateClass
        
        return leader[1]
    else:
        return None
    

################################### COMMANDS ###################################
class HtmlExportCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        scopeCache = {}
        previousSyntax = ''
        previousCssClass = ''

        colorScheme = view.options().get('colorscheme')
        theme = getTheme(colorScheme)
        CssScopes = getCssScopes(colorScheme)

        selRange = getSelectionRange(view)
        currentLineNumber = view.rowcol(selRange[0])[0]
        lineStartPts = getLineStartPts(view, *selRange)
        lnCols = `len(`view.rowcol(lineStartPts[-1]-1)[0]`)`
        lineNumbersTemplate = "<span class='lineNumber'>%"+ lnCols + "d  </span>"
        
        html = ["<pre class='%s'>" % theme]
        for pt in xrange(*selRange):
            if pt in lineStartPts:
                currentLineNumber +=1
                html.append(lineNumbersTemplate % currentLineNumber)
                
            scopeAtPt = view.syntaxName(pt)
            
            if scopeAtPt != previousSyntax:
                if scopeAtPt in scopeCache:
                    cssClassAtPt = scopeCache[scopeAtPt]
                else:
                    cssClassAtPt = getCssClassAtPt(pt, view, CssScopes)
                
                if previousCssClass != cssClassAtPt:
                    if scopeCache:
                        html.append("</span>")
                
                    if cssClassAtPt:
                        html.append("<span class='%s'>" % cssClassAtPt)
                
                scopeCache[scopeAtPt] = cssClassAtPt
                previousSyntax = scopeAtPt
                previousCssClass = cssClassAtPt
                
            html.append(cgi.escape(view.substr(pt)))
        
        html.append("</span></pre>")
        
        
        # Write out the css
        writeHTML("".join(html), view.fileName(), theme)
        writeCSS(colorScheme)
        
        # Open the file in browser
        htmlFile = "%s.html" % view.fileName()
        webbrowser.open(htmlFile)
        
        if OPEN_HTML_IN_EDITOR: view.window().openFile(htmlFile)