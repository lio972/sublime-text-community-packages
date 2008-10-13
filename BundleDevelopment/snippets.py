################################################################################

# Std Libs
from __future__ import with_statement

import os
import textwrap
import string

from itertools import takewhile

# Sublime Libs
import sublime
import sublimeplugin

################################################################################

SNIPPET_TEMPLATE = (
"""<!-- See http://www.sublimetext.com/docs/snippets for more information 
-->
<snippet>
    <content><![CDATA[%s]]></content>
</snippet>""" )

################################################################################

def consume(iterable, i=None):
    'Returns the last in an iterable or defaults to i if None in iterable'
    for i in iterable: pass
    return i

def contig(view, pt):
    if isinstance(pt, sublime.Region): pt = pt.begin()
    notAtBoundary = lambda p: view.substr(p) not in string.whitespace

    start = consume(takewhile(notAtBoundary, xrange(pt-1, -1, -1)),      pt)
    end   = consume(takewhile(notAtBoundary, xrange(pt, view.size())), pt-1)

    return sublime.Region(start, end + 1)
    
class DeleteTabTriggerAndInsertSnippetCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        tab_trigger = args[0]

        for sel in view.sel():
            start    =  max(sel.begin() - len(tab_trigger), 0)
            region   =  view.find(tab_trigger, start, 0)

            if region:  view.erase(region)
            else:       return

        view.runCommand('insertSnippet', args[1:])

class DeleteContigAndInsertSnippetCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        for sel in view.sel(): 
            view.erase(contig(view, sel))
            # print contig(view, sel), sel
        view.runCommand('insertSnippet', args)

class ExtractSnippetCommand(sublimeplugin.TextCommand):
    snippet = ''
    
    def run(self, view, args):
        sels = view.sel()

        # If we don't have at least two selections the command won't work
        if len(sels) < 2: return
    
        # Find the bounds of the text to extract as a snippet

        starts_at = sels[0].begin()
        ends_at = sels[-1].end()

        # Get the snippet text as an array of chars
        snippet = list ( view.substr(sublime.Region(starts_at, ends_at)))

        # Find all the tab stops: any selection that is not empty
        tab_stops = [ (s.begin(), s.end()) for s in sels if not s.empty()]

        # Replace all the tab stops with ${i:placeholder}
        adjustment = -starts_at

        for i, region in enumerate(tab_stops):
            adjusted_region = slice(region[0]+adjustment, region[1]+adjustment)

            replaced = snippet[adjusted_region]
            replacement = list('${%s:%s}' % (i, ''.join(replaced)))

            snippet[adjusted_region] = replacement

            adjustment += len(replacement) - len(replaced)

        # Turn the snippet char array into a string
        # Replace  softtabs with hard tabs for compatibility

        tab = (view.options().get('tabSize') or 8) * ' '
        snippet = (SNIPPET_TEMPLATE % ''.join(snippet)).replace(tab, '\t')

        # Save snippet file and open it
        development_snippet = os.path.join (
            sublime.packagesPath(),
            'BundleDevelopment',
            'development_snippet.sublime-snippet',
        )
        
        with open(development_snippet, 'w') as fh:
            fh.write(snippet)
        
        window = view.window()
        window.openFile(development_snippet)        
        
################################################################################

if __name__ == '__main__':
    unittest.main()