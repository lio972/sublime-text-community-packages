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

from columns import format_for_display

################################### SETTINGS ###################################

CREATE_FILES_FOR = ('sublime-keymap', 'sublime-options')

# see columns.py for quickpanel display settings

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

def wait_until_loaded(file):
    def wrapper(cb):
        view = sublime.activeWindow().openFile(file)
        if view.isLoading():
            sublime.addOnLoadedCallback(view, cb)
        else:
            cb(view)

    return wrapper

############################## INCREMENT TAB STOPS #############################

tab_stop_re = r"(?<!\\)\$(%s)|\$\{(%s):"
tab_stop = re.compile(tab_stop_re % ('\\d+', '\\d+'))

def inc_stop(m):
    return re.sub('\d+', lambda d: str(int(d.group()) + 1), m)

def increment_tabstops(s):
    return tab_stop.sub(lambda m: '%s' % inc_stop(m.group()), s)

def zero_stop(s, replace):
    return re.sub(replace, '0', s)

def replace_highest(s):
    h = str(max(int(max(g)) for g in tab_stop.findall(s)))
    
    return re.sub (
        tab_stop_re % (h,h),
        lambda m: '%s' % zero_stop(m.group(), h),
        s )

class IncrementTabstops(sublimeplugin.TextCommand):
    def run(self, view, args):
        for sel in view.sel():
            selection = view.substr(sel)
            view.replace(sel, replace_highest(increment_tabstops(selection)))

class WalkThroughSnippets(sublimeplugin.TextCommand):
    walker = None
    
    def run(self, view, args):
        if self.walker is None:
            self.walker = self.walk()

        try:
            self.walker.next()

        except StopIteration:
            sublime.messageBox('FINISHED')
            self.walker = None

        except Exception, e:
            self.walker = None
            raise

    def walk(self):
        for pkg, ext, f in glob_packages('sublime-snippet'):
            with open(f) as fh:
                s = fh.read()

                try:        dom = minidom.parseString(s)
                except:     pass
                else:
                    if  dom.getElementsByTagName('tabTrigger'):
                        continue

                    content = ''
                    for c in dom.getElementsByTagName('content'):
                        content = ''.join (
                            n.data for n in c.childNodes if n.nodeType in (3, 4))

                    if content.endswith('$0'): 
                        continue

            @wait_until_loaded(f)
            def and_then(view):
                regions  = []
                start_pt = 0

                # No god damn multi line find
                for rx in ('<content>', '</content>'):
                    regions.append(view.find(rx, start_pt))
                    if regions and regions[-1]: start_pt = regions[-1].end()

                if all(regions):
                    view.sel().clear()

                    view.sel().add(sublime.Region(
                        regions[0].end(),
                        regions[1].begin()
                    ))
                
            yield

################################################################################


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

def select(view, region):
    sel_set = view.sel()
    sel_set.clear()
    sel_set.add(region)
    view.show(region)

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

        display = format_for_display(args, cols = (0, 2, 3))

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

        display = format_for_display(options, cols= (0, 1) )

        def onSelect(i):
            window.openFile(*options[i][-2:])

        window.showSelectPanel(display, onSelect, None, 0, "", 0)

class ListCommands(sublimeplugin.WindowCommand):
    def finish(self, commands, display):
        window = sublime.activeWindow()

        def onSelect(i):
            window.openFile(*commands[i][-2:])

        window.showSelectPanel(display, onSelect, None, 0, "", 0)

    @sublimeplugin.threaded(finish=finish, msg='Be Patient!')
    def run(self, window, args):
        commands = []

        for pkg, module_name, f in glob_packages('py'):
            sublime.statusMessage('parsing %s' % module_name)
            commands += [
                (pkg, module_name, commandName(c.name), c.file, c.lineno) 
                for c in pyclbr.readmodule(module_name, [dirname(f)]).values()
                if 'sublimeplugin' in ''.join(unicode(b) for b in c.super)
            ]

        return commands, format_for_display(commands, cols=(0,1,2))

################################################################################