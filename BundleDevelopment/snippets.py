################################################################################

# Std Libs
from __future__ import with_statement
import os
import textwrap

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
        snippet = SNIPPET_TEMPLATE % ''.join(snippet)
        
        # Save snippet file and open        
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