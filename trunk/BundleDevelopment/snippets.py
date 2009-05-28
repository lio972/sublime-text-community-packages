################################################################################

# Std Libs
from __future__ import with_statement

import os
import textwrap
import string
import re
import functools
import datetime
import textwrap
import uuid
import shutil

from itertools import takewhile
from os.path import join, normpath, dirname, basename, splitext, split
from array import array

from xml.dom import minidom

from lxml import etree as ElementTree

# Sublime Libs
import sublime
import sublimeplugin

################################### SETTINGS ###################################

TIME_STAMPED = 0

SYMBOLIC_BINDINGS =  [ 'backquote', 'backslash', 'backspace',
					   'browser_back', 'browser_favorites', 'browser_forward',
					   'browser_home', 'browser_refresh', 'browser_search',
					   'browser_stop', 'capslock', 'clear', 'comma',
					   'contextmenu', 'delete', 'down', 'end', 'enter',
					   'equals', 'escape', 'home', 'insert', 'left',
					   'leftalt', 'leftbracket', 'leftcontrol', 'leftmeta',
					   'leftshift', 'leftsuper', 'minus', 'numlock',
					   'pagedown', 'pageup', 'pause', 'period', 'printscreen',
					   'quote', 'right', 'rightalt', 'rightbracket',
					   'rightsuper', 'scrolllock', 'semicolon', 'slash',
					   'space', 'tab', 'up' ]

################################################################################

SNIPPET_TEMPLATE = (
"""
<snippet>
<content><![CDATA[%(snippet)s$15]]></content>
<!-- 
scope:   %(scope)s
syntax:  %(syntax)s
project: %(project)s
package: %(package)s
filename: %(filename)s
-->

INSERT_META_HERE

<!--
Test PlayGround (Saver needs to parse) so do inside comments



-->                
</snippet>""" )

META = """
<meta>
    <name>${0:leave_blank_until_save}</name>
    <package>${1:%(package)s}${2:%(plugin_package)s}</package>
</meta>
<binding tab="${3:a,u,t,o,tab_unless_rename_attr_to_key}" 
         uuid="%(UUID)s"
         command="insertSnippet">
    <context name="selector" value="${4:%(base_scope)s} ${5:%(scope)s}"/>
</binding>$15
"""

############################# TIMESTAMPED FILENAMES ############################

def timestamped(file_name):
  """Puts a datestamp in file_name, just before the extension."""
  now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
  f, ext = splitext(file_name)
  return "%s-%s%s" % ( f, now, ext )

#################################### HELPERS ###################################

class Object(dict):
    __setattr__ = dict.__setitem__
    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError

def currentSyntaxPackage(view):
    return split(split(view.options().get("syntax"))[0])[1]

def get_package_dir(view):
        fn = view.fileName()
        if not fn: return

        return join( sublime.packagesPath(), currentSyntaxPackage(view) )

def parse_snippet(path):
    "('TEXT_NODE', 3) ('CDATA_SECTION_NODE', 4)"
    for c in minidom.parse(path).getElementsByTagName('content'):
        return ''.join(n.data for n in c.childNodes if n.nodeType in (3, 4))

class ParseAndInsertSnippetCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        f = normpath(join(split(sublime.packagesPath())[0], args[0]))
        view.runCommand('insertInlineSnippet', [parse_snippet(f)] + args[1:])

################################ REGION HELPERS ################################

def find_all(view, search, region, flags=0, P=None):
    pos = region.begin() #start position
    while True:
        r = view.find(search, pos, flags) #find next string
        if r is None or not region.contains(r) or pos >= region.end():
            break #string not found or past end of search area

        pos = r.end() #update current position

        if P is None or P(view, r):
            yield r

def expanded_selection_extents(view):
    sels = view.sel()
    return view.line(sels[0]).begin(), sels[-1].end()

################################## XML HELPERS #################################

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

################################ CREATE SNIPPET ################################

def escape_extents(view):
    """ Escapes characters that are `special` to snippet format """
    region = sublime.Region(*expanded_selection_extents(view))
    # Escaping $ Do it in reverse order to maintain selections
    escapes = sorted(find_all(view, r'\$', region)) 
    for r in reversed(escapes): view.insert(r.begin(), '\\')
    return escapes

def extract_snippet(view, hard_tabs = True):
    """ Does not escape selection """
    
    # Escape (reversed order)
    escapes = escape_extents(view)
    
    # Reset start end_points
    starts_at, ends_at = expanded_selection_extents(view)

    # Get array of characters
    substr = view.substr(sublime.Region(starts_at, ends_at))
    # Mutable: can set slices
    snippet = array('u', substr)

    # Find all the tab stops: any selection that is not empty
    tab_stops = [ (s.begin(), s.end()) for s in view.sel() if not s.empty()]

    # Replace all the tab stops with ${i:placeholder}
    adjustment = -starts_at
    
    tab_stop_map = {}


    for i, region in enumerate(tab_stops):
        adjusted_region = slice(region[0]+adjustment, region[1]+adjustment)

        replaced = ''.join(snippet[adjusted_region])
        tab_stop_index = tab_stop_map.get(replaced, i)
        
        replacement = array('u', '${%s:%s}' % (tab_stop_index, replaced))

        if tab_stop_index == i:
            tab_stop_map[replaced] = i

        snippet[adjusted_region] = replacement
        adjustment += len(replacement) - len(replaced)
    
    # Unescape
    for r in escapes: view.erase(r)
    
    snippet = textwrap.dedent(''.join(snippet))

    if hard_tabs:
        # Replace  softtabs with hard tabs for compatibility
        tab = (view.options().get('tabSize') or 8) * ' '
        snippet = snippet.replace(tab, '\t')

    return snippet

def save_snippet(view, snippet):
    # Get metadata ready for saving
    scope = list(reversed(view.syntaxName(view.sel()[0].begin()).strip().split()))
    base_scope = scope[0]    
    scope = ' '.join(scope[1:])

    fn = filename = view.fileName()
    
    pkg_path = sublime.packagesPath()
    if fn and pkg_path in fn:
        plugin_package = split(fn[len(pkg_path)+1:])[0]
    else:
        plugin_package = ''
    
    syntax = view.options().get('syntax')
    project = view.window().project()
    if project: project = project.fileName()
    package = dirname(syntax).split('/', 1)[1]
    UUID = uuid.uuid4()

    if not TIME_STAMPED: timestamped = lambda s: s  # noop

    development_snippet = timestamped(os.path.join (
        sublime.packagesPath(),
        'BundleDevelopment',
        'development_snippet.xml',
    ))

    with open(development_snippet, 'w') as fh:  
        snippet = SNIPPET_TEMPLATE % locals()
        fh.write(snippet)

    return development_snippet, META % locals()

############################## PARSE SNIPPET META ##############################

def parse_development_snippet(fn):
    et = ElementTree.parse(fn)
    root = et.getroot()
    meta = root.find('meta')
    binding = root.find('binding')
    if meta is None: return 
    return Object( (e.tag, e.text) for e in meta.getiterator() ), binding

def config_binding(binding, meta, snippet_name):
    tab = binding.get('tab')
    key = tab or binding.get('key')

    if ( tab ):
        key = ','.join(list(key) + ['tab'])

    binding.set('key', key)

    default = "insertSnippet '%(snippet_name)s'"
    command = binding.get('command', default) # TODO

    if command == 'insertSnippet': command = default
    binding.set('command', command % dict(snippet_name=snippet_name) )

    return binding

def pretty_dump_xml(et, fn):
    indent(et.getroot())
    et.write(fn, encoding='utf-8', pretty_print=True)

################################################################################

class ExtractSnippetCommand(sublimeplugin.TextCommand):
    snippet = ''

    def isEnabled(self, view, args):
        return args or len(view.sel()) > 1

    def onPostSave(self, view):
        fn = view.fileName()
        if not fn or not fn.endswith(('xml', 'sublime-snippet')): return

        meta, binding = parse_development_snippet(fn)
        if not meta or not (meta.name or meta.name):
            sublime.setTimeout (
                lambda: sublime.statusMessage('Found No Meta'), 20 )
            return

        UUID = binding.get('uuid')

        pkg_dir = join(sublime.packagesPath(), meta.package)
        snippet_name = join(pkg_dir, '%s.sublime-snippet' % meta.name)
        self.snippet = snippet_name

        window = view.window()

        if fn != snippet_name:
            shutil.copy(fn, snippet_name)
            sels = list(view.sel())

            def l8r():
                os.remove(fn)
                window.focusView(view)
                window.runCommand('close')
                window.openFile(snippet_name)

                active_view_sel = window.activeView().sel()
                active_view_sel.clear()
                for sel in sels:
                    active_view_sel.add(sel)

            sublime.setTimeout(l8r , 50)

        keymap =  join(pkg_dir, 'Default.sublime-keymap')
        window.openFile(keymap)
        window.openFile(snippet_name) #TODO

        et = ElementTree.parse(keymap)
        root = et.getroot()

        snippet_name = join('Packages', meta.package, basename(snippet_name))
        binding = config_binding(binding, meta, snippet_name.replace('\\', '/'))

        already_bound = root.xpath("binding[@uuid='%s']" % UUID)

        if already_bound:
            root.replace(already_bound[0], binding)
        else:
            root.append(binding)

        pretty_dump_xml(et, keymap)

    def test(self, view):
        if self.snippet:
            view.runCommand('insertInlineSnippet', [parse_snippet(self.snippet)])

    def run(self, view, args):
        if 'test' in args:  return self.test(view)

        snippet = extract_snippet(view)
        development_snippet, meta = save_snippet(view, snippet)        

        # Save snippet file, store path in instance var for `test` cmd
        self.snippet = development_snippet

        # Open for editing
        window = view.window()
        window.openFile(development_snippet)

        def insert():
            v = window.activeView()
            if v.fileName() == development_snippet:
                v.sel().clear()
                meta_region = v.find("INSERT_META_HERE", 0)
                v.erase(meta_region)
                v.sel().add(sublime.Region(meta_region.begin(), meta_region.begin()))
                v.runCommand('insertInlineSnippet', [meta])
            else:
                sublime.setTimeout(insert, 50)

        sublime.setTimeout(insert, 1)

################################################################################