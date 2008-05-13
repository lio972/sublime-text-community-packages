#################################### IMPORTS ###################################

from __future__ import with_statement

import sublime, sublimeplugin, os, sys, re, difflib
from os.path import split, join

################################### SETTINGS ###################################

DONT_CREATE_FILES = 0

################################### CONSTANTS ##################################

SUBLIME_KEYMAP = """
<!--
Bindable keys are:
(a-z, 0-9, f1-f15)
backquote, backslash, backspace, browser_back, browser_favorites, browser_forward,
browser_home, browser_refresh, browser_search, browser_stop, capslock, clear, comma,
contextmenu, delete, down, end, enter, equals, escape, home, insert, keypad0,
keypad1, keypad2, keypad3, keypad4, keypad5, keypad6, keypad7, keypad8, keypad9,
keypad_divide, keypad_enter, keypad_equals, keypad_minus, keypad_multiply,
keypad_period, keypad_plus, left, leftalt, leftbracket, leftcontrol, leftmeta,
leftshift, leftsuper, minus, numlock, pagedown, pageup, pause, period, printscreen,
quote, right, rightalt, rightbracket, rightsuper, scrolllock, semicolon, slash,
space, tab, up

Available modifiers are ctrl, alt, shift

Lines of the form "key1,key2 bind" will trigger when key1 is pressed, then key2 is
pressed. Make sure you don't include a space after the comma!

For example:
ctrl+x,ctrl+s save

New key bindings take effect as soon as you save this file, there's no need to
restart Sublime Text.

Also note that if the same key is bound twice, the last binding takes precedence
-->

<bindings>

</bindings>
"""

################################### FUNCTIONS ##################################

def getPackageDir(view):
    try: fn = view.fileName()
    except: return None
    
    pkgsPath = sublime.packagesPath()
    
    if fn and pkgsPath in fn: 
        pkgDir = split(fn[len(pkgsPath)+1:])[0]
    else:
        pkgDir = split(split(view.options().get("syntax"))[0])[1]
    
    return pkgDir

def openPreference(f, window):
    if not os.path.exists(f):
        if f.endswith('sublime-keymap'):
            toWrite = SUBLIME_KEYMAP

        elif f.endswith('sublime-options'):
            toWrite = None #'# sublime-options'
        else:       
            toWrite = None #"EditPreferenceCommand: created non existing file"
        
        if not DONT_CREATE_FILES and toWrite:
            with open(f, 'w') as fh:    
                fh.write(toWrite)
                
    window.openFile(f)

#################################### PLUGINS ###################################
    
class EditPreferenceCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        
        openPreference(
            join(sublime.packagesPath(), args[0]), window
        )

class EditPreferenceContextualCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        pkgDir = getPackageDir(window.activeView())
        if not pkgDir: return
        
        if args[0] == 'shortcutKeys':
            f = 'Default.sublime-keymap'
        
        elif args[0] == 'preferences':
            f = '%s.sublime-options' % pkgDir
        
        openPreference(
            os.path.normpath(join(sublime.packagesPath(), pkgDir, f)),
            window
        )

################################### SNIPPETS ###################################

snippetsRe = re.compile(r"Packages/.*?\.sublime-snippet", re.DOTALL | re.MULTILINE)

def findSnippets(path):
    snippets = []
    keyMaps = [f for f in os.listdir(path) if f.endswith('sublime-keymap')]

    for f in keyMaps:
        with open(join(path, f)) as fh:
            snippets += snippetsRe.findall(fh.read())
    
    return snippets

class EditSnippetCommand(sublimeplugin.TextCommand):
            
    def run(self, view, args):
        pkgDir = getPackageDir(view)
        if not pkgDir: return
        
        pkgDirAbs = os.path.normpath(join(sublime.packagesPath(), pkgDir))
        
        snippets = findSnippets(pkgDirAbs)
        
        if len(snippets) > 1:
            snippets = difflib.get_close_matches(args[0], 
                                                 [l.lower() for l in snippets], 
                                                 n=1,
                                                 cutoff=0.1)
        
        sublimeTextPath = split(sublime.packagesPath())[0]
        if snippets:
            for f in snippets:
                view.window().openFile(join(sublimeTextPath, f))

############################## LIST SHORTCUTS KEYS #############################

commands_regex = re.compile('<binding key="(.*?)".*?command="(.*?)"')

class ListShortcutKeysCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        mapping, clip = [], []
        
        for path, dirs, files in os.walk(sublime.packagesPath()):
            if path.endswith('.svn'): continue
            
            for f in files:
                if f.endswith('sublime-keymap'):
                    package = os.path.basename(path) + " ***"
                    mapping.append(("\n\n%30s: %s\n" % ("*** PACKAGE", package), ""))
                    with open(os.path.join(path, f)) as fh:
                        for lines in fh:
                            match = commands_regex.search(lines)
                            if match:
                                mapping.append(match.groups())
                                        
        for combo, command in mapping:
            if combo.startswith("\n"): clip.append(combo)
            else: clip.append("%30s: %s" % (combo, command))
        
        window.runCommand('new')
        window.activeView().insert(0, "\n".join(clip)[2:])
        
################################################################################