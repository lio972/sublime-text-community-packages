################################################################################

# Std Libs
from __future__ import with_statement

import os
import textwrap
import string
import re
import functools

from itertools import takewhile
from os.path import join, normpath, dirname, basename, splitext, split
from array import array

from xml.dom import minidom

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

        view.runCommand('insertSnippet', args[1:])

# class DeleteContigAndInsertSnippetCommand(sublimeplugin.TextCommand):
#     def run(self, view, args):
#         for sel in view.sel(): 
#             view.erase(contig(view, sel))
#             print contig(view, sel), sel
#         view.runCommand('insertSnippet', args)

def parse_snippet(path):
    "('TEXT_NODE', 3) ('CDATA_SECTION_NODE', 4)"
    for c in minidom.parse(path).getElementsByTagName('content'):
        return ''.join(n.data for n in c.childNodes if n.nodeType in (3, 4))

class ParseAndInsertSnippetCommand(sublimeplugin.TextCommand):
    cache = {}
    
    def run(self, view, args):
        f = normpath(join(split(sublime.packagesPath())[0], args[0]))
        if f not in self.cache: self.cache[f] = parse_snippet(f)
        view.runCommand('insertInlineSnippet', [self.cache[f]] + args[1:])
        
    def onPostSave(self, view):
        fn = view.fileName()
        if fn:
            if fn in self.cache: self.cache.pop(fn)

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
        snippet = array('u', view.substr(sublime.Region(starts_at, ends_at)))

        # Find all the tab stops: any selection that is not empty
        tab_stops = [ (s.begin(), s.end()) for s in sels if not s.empty()]

        # Replace all the tab stops with ${i:placeholder}
        adjustment = -starts_at

        for i, region in enumerate(tab_stops):
            adjusted_region = slice(region[0]+adjustment, region[1]+adjustment)

            replaced = snippet[adjusted_region]
            replacement = array('u', '${%s:%s}' % (i, ''.join(replaced)))

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
            'development_snippet.xml',
        )
        
        with open(development_snippet, 'w') as fh:  fh.write(snippet)
        window = view.window()
        window.openFile(development_snippet)
        
################################################################################

def getPackageDir(view):
    try: fn = view.fileName()
    except: return None
    
    return join (
       sublime.packagesPath(), split(split(view.options().get("syntax"))[0])[1]
    )
    
commands_regex = re.compile('<binding key="(.*?)".*?command="(.*?)"')
snippets_regex = re.compile("Packages/(.*?)\.sublime-snippet")

def parse_keymap(f):
    dom = minidom.parse(f)
    bindings = dom.getElementsByTagName('binding')
    
    for binding in bindings:
        key = binding.getAttribute('key')
        command = binding.getAttribute('command')
        
        tab_trigger = None 
        
        for context in binding.getElementsByTagName('context'):
            if context.getAttribute('name') == 'allPreceedingText':
                tab_trigger = context.getAttribute('value').rstrip('$')[2:]

        yield key, command, tab_trigger
                
def findSnippets(path):
    snippets = []
    keyMaps = [f for f in os.listdir(path) if f.endswith('sublime-keymap')]

    for f in (join(path, f) for f in keyMaps):
        for key, command, context in parse_keymap(f):
            if snippets_regex.search(command):
                snippets.append((context or key, command))

    return snippets

################################################################################

def snippetName(s):
    return basename(snippets_regex.search(s).group(1))

class SnippetQuickMenuCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        if args: 
            return self.quickOpen(args)

        window = view.window()

        snippetPath = getPackageDir(view)
        if snippetPath:
            snippets = findSnippets(snippetPath)
            if snippets:
                args = [`s` for s in snippets]
                display = [snippetName(s[1]) for s in snippets]
                self.view = view

                window.showQuickPanel('', 'snippetQuickMenu', args, display)
    
    def quickOpen(self, args):
        binding, command = eval(args[0])
        sublime.statusMessage(binding)
        self.view.runCommand(command)
        del self.view

################################################################################

if __name__ == '__main__':
    unittest.main()
    
################################################################################