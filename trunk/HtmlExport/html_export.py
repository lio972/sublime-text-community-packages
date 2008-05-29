#################################### IMPORTS ###################################

from __future__ import with_statement

from os.path import split, join, normpath, splitext

from plist import parse_plist

from build_css import camelizeString, getCSSFromThemeDict, getScopes

import sublime, sublimeplugin, cgi, webbrowser, time

################################### SETTINGS ###################################

OPEN_HTML_IN_EDITOR = 0

OPEN_HTML_IN_BROWSER = 1

COPY_CSS_TO_CLIPBOARD = 1                    # TODO make it a keybinding

COPY_HTML_TO_CLIPBOARD = 1

WRITE_OUT_HTML = OPEN_HTML_IN_EDITOR or OPEN_HTML_IN_BROWSER

ENCODE_AS = 'utf-8'

##################################### TODO #####################################

"""
    
    multiple selections, for posting snippets with foo() ... bar()      * done *
      
        contract selections so there are no empty lines 4 mult-sel
    

    outputting in new file just the html 
    
    pre tag + css to clipboard

    in <head> css styles

    embedded style="bla" attributes, no messing around with style
    sheets for quick posts
    
    line numbers in float:left pre tag so can easily copy paste
    
"""

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

LINE_NUMBER = '<span class="lineNumber">%s</span>'

################################### FUNCTIONS ##################################

def writeHTML(html, fn, theme):
    with open('%s.html' % fn, 'w') as fh:
        html = HTML_TEMPLATE % (fn, camelizeString(theme), html)
        fh.write(html.encode(ENCODE_AS))
    
    return '%s.html' % fn #TODO: refactor

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
        fh.write(css.encode(ENCODE_AS))
    
    return css   #TODO fix this

def getSelections(view):
    if view.hasNonEmptySelectionRegion():
        return [view.line(s) for s in view.sel()]
    else:
        return [sublime.Region(0, view.size())]

######################## SELECTOR SPECIFICITY FUNCTIONS ########################

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
        t = time.time()

        addLineNumbers = 'withLineNumbers' in args

        tab = ' ' * view.options().get('tabSize')

        scopeCache = {}
        previousScope = ''
        previousCssClass = ''

        colorScheme = view.options().get('colorscheme')
        theme = getThemeName(colorScheme)
        cssScopes = getCssScopes(colorScheme)

        html = ["<pre class='%s'>" % camelizeString(theme)]

        selections = getSelections(view)
        lnCols = len(`view.rowcol(selections[-1].end()-1)[0]`)
        
        for i, sel in enumerate(selections):
            if i > 0: html += [LINE_NUMBER % ("\n\n%s\n\n" % (lnCols * '.'))]

            if addLineNumbers:
                currentLineNumber = view.rowcol(sel.begin())[0] + 1          
                lineNumbersTemplate = LINE_NUMBER % ("%"+ `lnCols` + "d  ")
                html += [lineNumbersTemplate % currentLineNumber]

            for pt in xrange(sel.begin(), sel.end()):
                scopeAtPt = view.syntaxName(pt)
                if scopeAtPt != previousScope:
                    if scopeAtPt in scopeCache:
                        cssClassAtPt = scopeCache[scopeAtPt]
                    else:
                        cssClassAtPt = getCssClassAtPt(pt, view, cssScopes)

                    if previousCssClass != cssClassAtPt:
                        if previousCssClass: html.append("</span>")

                        if cssClassAtPt: # in case class is None
                            html.append("<span class='%s'>" % cssClassAtPt)

                    scopeCache[scopeAtPt] = cssClassAtPt
                    previousScope = scopeAtPt
                    previousCssClass = cssClassAtPt

                charAtPt = view.substr(pt)
                html += [cgi.escape(charAtPt.replace('\t', tab))]
                if addLineNumbers and charAtPt == '\n':
                    currentLineNumber += 1
                    html += [lineNumbersTemplate % currentLineNumber]

        html = "".join(html + ["</pre>"])
        sublime.statusMessage (
            "HTML and CSS conversion complete: %s " % (time.time() -t) +\
            "seconds, %s unique compound scopes." % len(scopeCache)
        )



        if WRITE_OUT_HTML:
            htmlFile = writeHTML(html, view.fileName(), theme)  # HACK TODO

        if OPEN_HTML_IN_BROWSER: webbrowser.open(htmlFile)
        if OPEN_HTML_IN_EDITOR: view.window().openFile()
        

        cssString = writeCSS(colorScheme)    # HACK TODO.. 
                                             # and the rest isnt??  hahahah

        clipboard = ''
        if COPY_CSS_TO_CLIPBOARD: clipboard += cssString
        if COPY_HTML_TO_CLIPBOARD: clipboard += html
        if clipboard:
            sublime.setClipboard(clipboard)
        
        print clipboard
################################################################################