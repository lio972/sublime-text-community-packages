#################################### IMPORTS ###################################

# Std Libraries
from __future__ import with_statement

import os
import glob
from os.path import split, splitext, join, normpath, abspath, isdir, basename, dirname

import sys
import re
import difflib
import pyclbr

from xml.dom import minidom

# Sublime Modules
import sublime
import sublimeplugin
from sublimeplugin import commandName

################################### SETTINGS ###################################

CREATE_FILES_FOR = ('sublime-keymap')#, 'sublime-options')

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

#################################### PLUGINS ###################################

class EditPackageFiles(sublimeplugin.WindowCommand):
    def run(self, window, args):
        pref_type = args[0]
        
        pkg_path = sublime.packagesPath()
        files = []

        for pkg in contextual_packages_list(window.activeView()):
            path_joins = [pkg_path, pkg, '*.%s' % pref_type]
            if pkg == 'Default' and pref_type == 'sublime-options':
                path_joins.insert(2, 'Options')

            found_files = glob.glob(join(*path_joins ))
            if not found_files and pref_type in CREATE_FILES_FOR:
                found_files.append(
                    join (
                        pkg_path, pkg , "%s.%s" % (
                            'Default' if pref_type == 'sublime-keymap' 
                             else pkg, pref_type)
                    )
                )

            files.extend (
                [(pkg, splitext(basename(f))[0], f) for f in found_files] )

        display = [
            (("%s: %s" % f[:2]) if pref_type != 'sublime-keymap'
                                and f[0] != f[1] 
                                else f[0]) + (' (create)' if not os.path.exists(f[2]) else '')
            for f in files 
        ]

        sublime.statusMessage('Please choose %s file to %s' % (
            args[0], ' '.join(args[1:]) or 'edit')
        )

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

############################## LIST SHORTCUTS KEYS #############################

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

class ListShortcutKeysCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        args = []

        pkg_path = sublime.packagesPath()
        pkg_list = contextual_packages_list(window.activeView())

        for pkg in pkg_list:
            keymaps = glob.glob(join(pkg_path, pkg,  "*.sublime-keymap"))

            for f in keymaps:
                try:
                    for key, command in parse_keymap(f):
                        args.append((pkg, f, key, command))
                except Exception, e:
                    print f

        pkg_format = "%" + `max(len(f) for f in pkg_list)` + 's'

        display = [
            ("%s %30s: %s" % (pkg_format % f[0], f[2], f[3])) for f in args ]

        def onSelect(i):
            f = args[i]

            @wait_until_loaded(f[1])
            def and_then(view):
                region = view.find(f[3], 0, sublime.LITERAL)
                if region:
                    region = view.find(f[2], 
                        view.line(region).begin(), sublime.LITERAL)
 
                    if region:
                        select(view, region)

        def onCancel():
            pass
        
        window.showSelectPanel(display, onSelect, onCancel, 0, "", 0)
        
################################################################################

class ListCommands(sublimeplugin.WindowCommand):
    def run(self, window, args):
        pkg_path = sublime.packagesPath()
        
        pkg_list = contextual_packages_list()
        
        commands = []

        for pkg in pkg_list:
            modules = glob.glob(join(pkg_path, pkg, '*.py'))
            
            for m in modules:
                path = [dirname(m)]
                module_name = splitext(basename(m))[0]
                
                commands += [
                    (pkg, module_name, commandName(c.name), c.file, c.lineno) 
                    for c in pyclbr.readmodule(module_name, path).values()
                    if 'sublimeplugin' in ''.join(unicode(b) for b in c.super)
                ]

        pkg_format = "%" + `max(len(f) for f in pkg_list)+2` + 's'
        m_format = "%" + `max(len(c[1]) for c in commands)+2` + 's'
        c_format = "%" + `max(len(c[2]) for c in commands)+2` + 's'
        
        display = [ "%s %s %s" % ( pkg_format % c[0], 
                                   m_format % c[1],
                                   c_format % c[2]) 
                    
                    for c in commands ]

        def onSelect(i):
            arg = commands[i]
            window.openFile(arg[-2], arg[-1])

        def onCancel():
            pass
        
        window.showSelectPanel(display, onSelect, onCancel, 0, "", 0)

################################################################################