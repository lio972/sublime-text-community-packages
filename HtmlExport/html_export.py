from __future__ import with_statement
import sublime, sublimeplugin, cgi, re, webbrowser

from os.path import split, join, normpath, splitext

import plist, build_css

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

def writeHTML(html, fn, theme):
    with open('%s.html' % fn, 'w') as fh:
        fh.write(HTML_TEMPLATE % (fn, theme, html))

def writeCSS(colorScheme, theme):
    appdataPath = split(sublime.packagesPath())[0]
    themePList = normpath(join(appdataPath, colorScheme))
    css = build_css.getCSSFromThemeDict(plist.parse_plist(themePList))
    with open("%s.css" % theme, 'w') as fh:
        fh.write(re.sub(r"\.py\b", '.python', css))    

def getLineStarts(view, start, end):
    pt, lines  = start, [start]
    while pt < end:
        pt = view.line(pt).end()+1
        lines.append(pt)
    return lines

class HtmlExportCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        colorScheme = view.options().get('colorscheme')
        theme = splitext(split(colorScheme)[1])[0]

        
        sel = view.sel()[0]
        if not sel.empty():
            selRange = view.line(sel)
            selRange = selRange.begin(), selRange.end()
        else:
            selRange = 0, view.size()
        
        currentScope = []
        line = view.rowcol(selRange[0])[0]
        linesStart = getLineStarts(view, *selRange)

        cols = `len(`view.rowcol(linesStart[-1]-1)[0]`)`
        lineNumbersTemplate = "<span id='line-number'>%"+ cols + "d  </span>"
        
        html = ["<pre class='sublime %s'>" % theme]
        currentSyntax = ''
        for pt in xrange(*selRange):
            
            if pt in linesStart:
                line+=1
                html.append(lineNumbersTemplate % line)
            
            syntaxAtPoint = view.syntaxName(pt)
            if syntaxAtPoint != currentSyntax:
                scopes = reversed(syntaxAtPoint.split(" "))
                scopes = [' '.join(s.split('.')) for s in scopes if s]

                if currentScope:
                    diverge = None
                    for i, s in enumerate(currentScope):
                        if i >= len(scopes) or scopes[i] != s:
                            if not diverge: diverge = i
                            html.append("</span>")

                    currentScope = currentScope[:diverge]

                for s in scopes[len(currentScope):]:
                    currentScope.append(s)
                    html.append("<span class='%s'>" % s)

                currentSyntax = syntaxAtPoint

            html.append(cgi.escape(view.substr(pt)))

        html.append("</span></pre>")
        
        writeHTML("".join(html), view.fileName(), theme)
        writeCSS(colorScheme, theme)
        
        htmlFile = "%s.html" % view.fileName()
        webbrowser.open(htmlFile)
        view.window().openFile(htmlFile)