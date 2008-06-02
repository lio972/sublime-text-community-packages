#################################### IMPORTS ###################################

from __future__ import with_statement, division

from os.path import split, join, normpath, splitext

from plist import parse_plist

from build_css import camelizeString, getCSSFromThemeDict, getScopes

import sublime, sublimeplugin, cgi, webbrowser, time

################################### SETTINGS ###################################

OPEN_HTML_IN_EDITOR = 0

OPEN_HTML_IN_BROWSER = 1

COPY_CSS_TO_CLIPBOARD = 1                            # TODO make it a keybinding

COPY_HTML_TO_CLIPBOARD = 1

WRITE_OUT_HTML = OPEN_HTML_IN_EDITOR or OPEN_HTML_IN_BROWSER

ENCODE_AS = 'utf-8'

##################################### TODO #####################################

"""
    clean up 4 000,000 line function
    
    work on - and || operators for scopes
    
    
    multiple selections, for posting snippets with foo() ... bar()      = DONE =
      
        contract selections so there are no empty lines 4 mult-sel
    

    pre tag + css to clipboard                                   = almost DONE =

    compress clipboard css                                              = DONE =
    
    embedded style="bla" attributes, no messing around with style
    sheets for quick posts
    
    in <head> css styles

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

def getCssRules(colorScheme):
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

# http://manual.macromates.com/en/scope_selectors.html#ranking_matches

# TODO    -  operator           source - source.python
#         || operator           source - (source.python || source.ruby)   

def leveledScopes(scope):
    scope = ' '.join(scope.split(' -')[:1])
    scope = [l.strip() for l in scope.split(' ')]
    return [l.split('.') for l in scope]

def selectorSpecificity(selector, scope):
    allSelectors, allScopes = map(leveledScopes, (selector, scope))

    specificity = [None] * len(allSelectors)
    for i, selectors in enumerate(allSelectors):
        for scopeLevel, scopes in enumerate(allScopes):
            if not [s for s in selectors if s not in scopes]:
                specificity[i] = (scopeLevel+1, len(selectors))
        
        if not specificity[i]: return []

    return specificity

def compareCandidates(c1, c2):
    cd1, cd2 = c1[0][:], c2[0][:]

    while cd1 and cd2:
        either_is_greater = cmp(cd1.pop(), cd2.pop())
        if either_is_greater: return either_is_greater

    return cmp(cd1, cd2)

def sortCandidates(candidates):
    return sorted(candidates, compareCandidates)

def getCssClassAtPt(pt, view, cssRules):
    candidates = []
    scopeAtPoint = " ".join(reversed(view.syntaxName(pt).split()))

    for cssClass, selectors in cssRules.items():
        for selector in selectors:
            specificity = selectorSpecificity(selector, scopeAtPoint)
            if specificity:
                candidates.append((specificity, cssClass))

    if candidates:
        candidates = sortCandidates(candidates)
        return candidates[-1][1]

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
        cssRules = getCssRules(colorScheme)

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
                        cssClassAtPt = getCssClassAtPt(pt, view, cssRules)

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

        cssString = writeCSS(colorScheme)    # HACK TODO

        clipboard = ''
        if COPY_CSS_TO_CLIPBOARD: 
            # compress the css
            css = ' '.join([l.strip('\n') for l in cssString.split('\n')])
            clipboard += ' '.join([w.strip(' ') for w in css.split(' ')]) + '\n'
            
        if COPY_HTML_TO_CLIPBOARD: clipboard += html
        if clipboard:
            sublime.setClipboard(clipboard)
        
################################################################################