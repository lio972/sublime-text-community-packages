#################################### IMPORTS ###################################

from __future__ import with_statement
import sublime, sublimeplugin, cgi, re, webbrowser

from os.path import split, join, normpath, splitext

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
    pre {padding: 1em; font: 12px "DejaVu Sans Mono";}
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

def writeCSS(colorScheme, theme):
    appdataPath = split(sublime.packagesPath())[0]
    themePList = normpath(join(appdataPath, colorScheme))
    css = build_css.getCSSFromThemeDict(plist.parse_plist(themePList))
    with open("%s.css" % theme, 'w') as fh:
        fh.write(re.sub(r"\.py\b", '.python', css))    

def getLineStartPts(view, start, end):
    pt, lines  = start, [start]
    while pt < end:
        pt = view.line(pt).end()+1
        lines.append(pt)
    return lines

def getSelectionRange(view):
    sel = view.sel()[0]
    if not sel.empty():
        expanded = view.line(sel)
        return expanded.begin(), expanded.end()
    else:
        return 0, view.size()

################################### COMMANDS ###################################

class HtmlExportCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        colorScheme = view.options().get('colorscheme')
        theme = splitext(split(colorScheme)[1])[0]
        
        selRange = getSelectionRange(view)
        
        currentScopes = []
        currentLineNumber = view.rowcol(selRange[0])[0]
        lineStartPts = getLineStartPts(view, *selRange)

        lnCols = `len(`view.rowcol(lineStartPts[-1]-1)[0]`)`
        lineNumbersTemplate = "<span id='line-number'>%"+ lnCols + "d  </span>"
        
        html = ["<pre class='sublime %s'>" % theme]
        previousSyntax = ''
        for pt in xrange(*selRange):
            
            if pt in lineStartPts:
                currentLineNumber +=1
                html.append(lineNumbersTemplate % currentLineNumber)
            
            syntaxAtPoint = view.syntaxName(pt)
            if syntaxAtPoint != previousSyntax:
                newScopes = reversed(syntaxAtPoint.split(" "))
                newScopes = [' '.join(s.split('.')) for s in newScopes if s]

                if currentScopes:
                    diverged = None
                    for i, s in enumerate(currentScopes):
                        if i >= len(newScopes) or newScopes[i] != s:
                            if not diverged: diverged = i
                            html.append("</span>")

                    currentScopes = currentScopes[:diverged]

                for s in newScopes[len(currentScopes):]:
                    currentScopes.append(s)
                    html.append("<span class='%s'>" % s)

                previousSyntax = syntaxAtPoint

            html.append(cgi.escape(view.substr(pt)))
        
        
        html.append("</span></pre>")
        
        writeHTML("".join(html), view.fileName(), theme)
        writeCSS(colorScheme, theme)
        
        htmlFile = "%s.html" % view.fileName()
        webbrowser.open(htmlFile)
        
        if OPEN_HTML_IN_EDITOR: view.window().openFile(htmlFile)