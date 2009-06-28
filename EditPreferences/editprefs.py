#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libraries
from __future__ import with_statement

import sys
import glob
import os
import pprint
import cgi
import re
import pyclbr

from os.path import ( split, splitext, join, normpath, abspath, isdir,
                      basename, dirname )

# 3rd Party Libs
from lxml.etree import parse

# Sublime Modules
import sublime
import sublimeplugin

# Sublime plugin helpers
from sublimeplugin import commandName
from pluginhelpers import threaded, wait_until_loaded, asset_path, do_in, select
from quickpanelcols import format_for_display
from sublimeconstants import LITERAL_SYMBOLIC_BINDING_MAP
from tmscopes import selector_specificity, compare_candidates, normalize_scope

################################### SETTINGS ###################################

CREATE_FILES_FOR = ('sublime-keymap', 'sublime-options')

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
    root = parse(f).getroot()
    bindings = root.xpath('binding')

    for binding in bindings:
        key = binding.get('key')
        command = binding.get('command')

        scope = binding.xpath('context[@name="selector"][1]/@value')

        if scope:
            scope = scope[0]
        else:
            scope = 'source,plain'

        yield key, command, scope, binding.sourceline

def get_contextual_packages(view):
    try: fn = view.fileName()
    except: return []

    pkg_path = sublime.packagesPath()
    dirs = []

    if fn and pkg_path in fn:
        dirs.append(split(fn[len(pkg_path)+1:])[0])

    dirs.append(split(split(view.options().get("syntax"))[0])[1])

    return dirs

def normalize_tabtriggers(key):
    if key.endswith(',tab'):
        key = ''.join(key[:-4].split(',')) + '<tab>'

    return key

def normalize_modifier_sequencing(key):
    rebuilt_key = []

    for combo in key.split(','):
        keys = combo.split('+')
        rebuilt_combo = []

        for mod in ('ctrl', 'alt', 'shift'):
            if mod in keys:
                rebuilt_combo.append(keys.pop(keys.index(mod)))

        rebuilt_combo.extend(keys)
        rebuilt_key.append('+'.join(rebuilt_combo))

    return ','.join(rebuilt_key)


def normalize_binding_display(key):
    return normalize_tabtriggers(normalize_modifier_sequencing(key))

################################################################################

def contextual_packages_list(view=None):
    if view is None:
        view = sublime.activeWindow().activeView()

    contextual = get_contextual_packages(view)
    pkg_path = sublime.packagesPath()

    others = sorted((f for f in os.listdir(pkg_path) if isdir(join(pkg_path, f))
                       and not f in contextual), key = lambda f: f.lower())

    return contextual + others

def open_preference(f, window):
    if not os.path.exists(f):
        if f.endswith('sublime-keymap'):
            to_write = SUBLIME_KEYMAP

        elif f.endswith('sublime-options'):
            to_write = '# sublime-options'
        else:
            to_write = None #"EditPreferenceCommand: created non existing file"

        if splitext(f)[1][1:] in CREATE_FILES_FOR and to_write:
            with open(f, 'w') as fh:
                fh.write(to_write)

    window.openFile(f)

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
                ( sublime.options().get('keymap') if
                  file_type == 'sublime-keymap' else pkg ),
                file_type)
            ))

        for f in found_files:
            yield pkg, splitext(basename(f))[0], f

#################################### PLUGINS ###################################

class SyntaxToScopeMap(object): # disabled by object inheritance
    def run(self, view, args):
        mapping = {}
        bases = []

        for pkg, basename, f in glob_packages('tmLanguage'):
            bases.append(basename)
            scope_path = ( 'dict/key[.="scopeName"]'
                           '/following-sibling::*[1]'
                           '/text()' )

            root = lxml.etree.parse(f).getroot()
            scope = root.xpath(scope_path)

            f = 'Packages' + f[len(sublime.packagesPath()):].replace('\\','/')

            if scope:
                mapping[f] = scope[0]

class EditPackageFiles(sublimeplugin.WindowCommand):
    def run(self, window, args):
        pref_type = args[0]
        files = list(glob_packages(pref_type))
        keymap = sublime.options().get('keymap')

        if pref_type == 'sublime-keymap':
            display = [(
                (' + ' if not os.path.exists(f[2]) else ''),
                f[0],
                f[1] if f[1] != keymap else '')
                for f in files ]
        else:
            display = [
                ((' + ' if not os.path.exists(f[2]) else ''),
                f[0],
                f[1] if f[0] != f[1] else '')
                for f in files ]

        if all(not r[0] for r in display):
            display = [r[1:] for r in display]

        display = format_for_display(display)

        sublime.statusMessage (
        'Please choose %s file to %s' % (args[0], ' '.join(args[1:]) or 'edit'))

        def onSelect(i):
            f = files[i][2]

            if len(args) == 1:
                open_preference( f, window)
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

        keymaps = glob_packages('sublime-keymap')

        for pkg, name, f in keymaps:
            if not os.path.exists(f): continue
            try:
                for key, command, scope, line in parse_keymap(f):
                    nkey = normalize_binding_display(key)
                    args.append((pkg, f, key, nkey, command, line, scope))

            except Exception, e:
                print e, f

        view = window.activeView()
        scope = normalize_scope( view.syntaxName(
                                 view.sel()[0].begin() ))
        args = sorted (
            args,
            key = lambda t: selector_specificity(t[-1], scope ),
            cmp = compare_candidates,
            reverse = True )

        def onSelect(i):
            f, key, nkey, command, line, scope = args[i][1:7]

            @wait_until_loaded(f)
            def and_then(view):
                regions = [view.line( view.textPoint(int(line)-1, 0) -1 )]

                for search in (key, ):
                    search = cgi.escape(search)
                    new_reg = view.find (
                            search, view.line(regions[-1]).begin(),
                            sublime.LITERAL )

                    if new_reg:
                        regions.append (new_reg)
                    else:
                        break

                for region in regions[-1:]:
                    select(view, region)

        display = format_for_display(args, cols = (0, 3, 4))
        window.showSelectPanel(display, onSelect, None, 0, "", 0)

################################################################################

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

################################################################################

class InsertBindingRepr(sublimeplugin.TextCommand):
    def run(self, view, (insertion, )):
        start_pt = view.sel()[0].begin() + len(insertion)
        view.runCommand('insertAndDecodeCharacters', [insertion])

        @do_in(0)
        def l8r():
            binding_region = sublime.Region(start_pt, view.sel()[0].begin() )
            binding = view.substr( binding_region )

            view.erase ( binding_region)
            view.runCommand('insertAndDecodeCharacters',
                [LITERAL_SYMBOLIC_BINDING_MAP.get(binding, binding)]
            )

class CreatePluginBinding(sublimeplugin.TextCommand):
    def run(self, view, args):
        plugname = commandName( view.substr(view.word(view.sel()[0])))
        binding = '<binding key="" command="%s">\t\n</binding>' % plugname
        view.cb = binding

################################################################################

class ListCommands(sublimeplugin.WindowCommand):
    def finish(self, commands, display):
        window = sublime.activeWindow()

        def onSelect(i):
            window.openFile(*commands[i][-2:])

        window.showSelectPanel(display, onSelect, None, 0, "", 0)

    @threaded(finish=finish, msg='Be Patient!')
    def run(self, window, args):
        commands = []

        for pkg, module_name, f in glob_packages('py'):
            sublime.statusMessage('parsing %s' % module_name)
            commands += [
                (pkg, module_name, commandName(c.name), c.file, c.lineno)
                for c in pyclbr.readmodule(module_name, [dirname(f)]).values()
                if any( p in ''.join(unicode(b) for b in c.super) for p in
                    ( 'TextCommand', 'Plugin', 'WindowCommand',
                      'ApplicationCommand', 'sublimeplugin' ))
            ]

        return commands, format_for_display(commands, cols=(0,1,2))

################################################################################