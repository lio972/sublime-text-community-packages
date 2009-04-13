#################################### IMPORTS ###################################

# Std Libraries
from __future__ import with_statement

import sys

import os
import glob
from os.path import ( split, splitext, join, normpath, abspath, isdir, 
                      basename, dirname )

from itertools import chain
from collections import defaultdict
import mmap

from math import ceil

import re
import difflib

import pyclbr

from xml.dom import minidom

# Sublime Modules
import sublime
import sublimeplugin
from sublimeplugin import commandName

################################### SETTINGS ###################################

CREATE_FILES_FOR = ('sublime-keymap', 'sublime-options')

SCREEN_WIDTH = 150  # char width of quick panel (select then copy => status)

CELL_PADDING = 4

################################### CONSTANTS ##################################

SUBLIME_KEYMAP = """
<!--
Bindable keys are:
(a-z, 0-9, f1-f15)

backquote, backslash, backspace, browser_back, browser_favorites,
browser_forward, browser_home, browser_refresh, browser_search, browser_stop,
capslock, clear, comma, contextmenu, delete, down, end, enter, equals, escape,
home, insert, left, leftalt, leftbracket, leftcontrol, leftmeta, leftshift,
leftsuper, minus, numlock, pagedown, pageup, pause, period, printscreen, quote,
right, rightalt, rightbracket, rightsuper, scrolllock, semicolon, slash, space,
tab, up

Available modifiers are ctrl, alt, shift.

Lines of the form "key1,key2 bind" will trigger when key1 is pressed, then key2
is pressed.

For example:
<binding key="ctrl+x,ctrl+s" command="save"/>


New key bindings take effect as soon as you save this file, there's no need to
restart Sublime Text.

Also note that if the same key is bound twice, the last binding takes precedence
-->

<bindings>

</bindings>
"""

################################### FUNCTIONS ##################################

def parse_keymap(f):
    dom = minidom.parse(f)
    bindings = dom.getElementsByTagName('binding')

    for binding in bindings:
        key = binding.getAttribute('key')
        command = binding.getAttribute('command')

        yield key, command

def get_contextual_packages(view):
    try: fn = view.fileName()
    except: return []

    pkg_path = sublime.packagesPath()
    dirs = []

    if fn and pkg_path in fn: 
        dirs.append(split(fn[len(pkg_path)+1:])[0])
    
    dirs.append(split(split(view.options().get("syntax"))[0])[1])
    
    return dirs

def contextual_packages_list(view=None):
    if view is None:
        view = sublime.activeWindow().activeView()

    contextual = get_contextual_packages(view)
    pkg_path = sublime.packagesPath()
    
    others = sorted((f for f in os.listdir(pkg_path) if isdir(join(pkg_path, f)) 
                        and not f in contextual), key = lambda f: f.lower())
    
    return contextual + others

def openPreference(f, window):
    if not os.path.exists(f):
        if f.endswith('sublime-keymap'):
            toWrite = SUBLIME_KEYMAP

        elif f.endswith('sublime-options'):
            toWrite = '# sublime-options'
        else:
            toWrite = None #"EditPreferenceCommand: created non existing file"
        
        if splitext(f)[1][1:] in CREATE_FILES_FOR and toWrite:
            with open(f, 'w') as fh:    
                fh.write(toWrite)

    window.openFile(f)

def asset_path(f):
    pkg_path = sublime.packagesPath()
    return join('Packages', f[len(pkg_path)+1:]).replace("\\", '/')

def glob_packages(file_type='sublime-keymap', view=None):
    pkg_path = sublime.packagesPath()

    for pkg in contextual_packages_list(view):
        path_joins = [pkg_path, pkg, '*.%s' % file_type]
        if pkg == 'Default' and file_type == 'sublime-options':
            path_joins.insert(2, 'Options')
        
        found_files = glob.glob(join(*path_joins))
        
        if not found_files and file_type in CREATE_FILES_FOR:
            found_files.append ( join (
                pkg_path, pkg , "%s.%s" % (
                'Default' if file_type == 'sublime-keymap' else pkg, 
                file_type)
            ))

        for f in found_files:
            yield pkg, splitext(basename(f))[0], f

def wait_until_loaded(file):
    def wrapper(f):
        sublime.addOnLoadedCallback(file, f)
        sublime.activeWindow().openFile(file)

    return wrapper

def select(view, region):
    sel_set = view.sel()
    sel_set.clear()
    sel_set.add(region)
    view.show(region)

############################### COLUMN RENDERING ###############################

def pop(l, ix, default):
    try:               return l.pop(ix)
    except IndexError: return default

def find_widths(columns, total_width=SCREEN_WIDTH, cell_padding=CELL_PADDING):
    O = int(len(columns[0]) / 10)

    # Find the average, discarding some outliers
    seq =  [ (sum(len(element) for element in L) /len(L)) for L in   
             [sorted(S)[O:len(S)-O] for S in columns] ]

    n = len(columns)
    screen_width = total_width - n * cell_padding  # padded by render_rows func

    # Inverse square scaling; smaller get more share
    scaling = [(float((x ** -0.5) * screen_width)/sum(seq)) for x in seq]
    seq = [x*y for x,y in zip(scaling, seq)]

    column_widths = [ int(x*screen_width/sum(seq))  for x in seq]

    for i, col in enumerate(columns):
        colw = column_widths.pop(0)
        maxw = max(len(l) for l in col)
        width = min(maxw, colw)

        if maxw < colw:
            remaining_cols = columns[i+1:]
            remaining_width = abs( maxw - colw ) + sum(column_widths)
            if remaining_cols:
                column_widths = list( 
                    find_widths(remaining_cols, remaining_width, 0))

        yield width

def pad_columns(columns, align=unicode.ljust):
    padded = []
    
    for i, (col, width) in enumerate(zip(columns, find_widths(columns))):
        def ellipsis(s):
            return ( s if (len(s) <= width or i+1 == len(columns)) 
                     else s[:width-3] + ' ..')

        padded.append([align(unicode(ellipsis(c.strip())), width) for c in col ])
    
    return padded

def columns_2_rows(columns): # [[], [], []]
    return [tuple(a[i] for a in columns) for i in xrange(len(columns[0]))]

def rows_2_columns(rows):
    [ [r[i] for r in rows] for i,_ in enumerate(rows[0])]

def rendered_rows(rows, pl=0, pr=CELL_PADDING):
    pad = lambda r: [(pl*' ') + c + (pr*' ') for c in r]
    return [''.join(pad(r)) for r in rows]

def format_for_display(args, ix, no_space=()):
    columns = [ [a[i] for a in args] for i in chain(ix, no_space) ]
    return rendered_rows(columns_2_rows(pad_columns(columns)))

#################################### PLUGINS ###################################

class EditPackageFiles(sublimeplugin.WindowCommand):
    def run(self, window, args):
        pref_type = args[0]
        files = []

        for pkg, name, f in glob_packages(pref_type):
            files.append((pkg, name, f))

        display = [
            (("%s: %s" % f[:2]) if pref_type != 'sublime-keymap' and f[0] != f[1]
            
                else ( 
                    f[0]) + (' (create)' if not os.path.exists(f[2]) else '') )

            for f in files ]
        
        sublime.statusMessage (
         'Please choose %s file to %s' % (args[0], ' '.join(args[1:]) or 'edit'))

        def onSelect(i):
            f = files[i][2]

            if len(args) == 1:
                openPreference( f, window)
            else:
                cmd = args[1]
                cmd_args = args[2:] + [asset_path(f)]

                sublime.activeWindow().activeView().runCommand(cmd, cmd_args )

        def onCancel(): pass

        window.showSelectPanel(display, onSelect, onCancel, 
          sublime.SELECT_PANEL_MULTI_SELECT, "", 0)


###################### LIST SHORTCUT KEYS COMMANDS OPTIONS #####################

class ListShortcutKeysCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        args = []

        for pkg, name, f in glob_packages('sublime-keymap'):
            if not os.path.exists(f): continue
            try:
                for key, command in parse_keymap(f):
                    args.append((pkg, f, key, command))
            except Exception, e:
                print e, f

        def onSelect(i):
            f, key, command = args[i][1:]

            @wait_until_loaded(f)
            def and_then(view):
                regions = [sublime.Region(0, 0)]

                for search in command, key:
                    regions.append (
                        view.find (
                            search, view.line(regions[-1]).begin(), 1)
                    )

                for region in regions[-1:]:
                    select(view, region)

        display = format_for_display(args, (0, 2, 3,))

        window.showSelectPanel(display, onSelect, None, 0, "", 0)

class ListOptions(sublimeplugin.WindowCommand):
    def run(self, window, args):
        options = []

        for pkg, name, f in glob_packages('sublime-options'):
            if not os.path.exists(f): continue
            pkg_display = "%s - %s" % (pkg, name) if name != pkg else pkg
            with open(f) as fh:
                for i, line in enumerate(fh):
                    if line.strip() and not line.startswith('#'):
                        options.append (
                            (pkg_display, line.strip(), f, i + 1) )

        display = format_for_display(options, [0], [1] )

        def onSelect(i):
            window.openFile(*options[i][-2:])

        window.showSelectPanel(display, onSelect, None, 0, "", 0)

class ListCommands(sublimeplugin.WindowCommand):
    def finish(self, commands):
        display = format_for_display(commands, [0,1,2])
        window = sublime.activeWindow()

        def onSelect(i):
            window.openFile(*commands[i][-2:])

        window.showSelectPanel(display, onSelect, None, 0, "", 0)
    
    
    def run(self, window, args):
        commands = []

        for pkg, module_name, f in glob_packages('py'):
            sublime.statusMessage('parsing %s' % module_name)
            commands += [
                (pkg, module_name, commandName(c.name), c.file, c.lineno) 
                for c in pyclbr.readmodule(module_name, [dirname(f)]).values()
                if 'sublimeplugin' in ''.join(unicode(b) for b in c.super)
            ]

        return commands
        
    try:
        # Requires AAALoadfirstExtensions
        run = sublimeplugin.threaded(finish=finish, msg='Be Patient!')(run)
    except Exception, e:
        pass

################################################################################