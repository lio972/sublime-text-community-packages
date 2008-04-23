from __future__ import with_statement

import sublime, sublimeplugin, os, sys, re

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

def openPreference(f, window):
    if not os.path.exists(f):
        with open(f, 'w') as fh:
            if f.endswith('sublime-keymap'):
                toWrite = SUBLIME_KEYMAP
            elif f.endswith('sublime-options'):
                toWrite('# sublime-options')
            else:                
                fh.write("EditPreferenceCommand: created non existing file")
    window.openFile(f)
    
class EditPreferenceCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        
        openPreference(
            os.path.join(sublime.packagesPath(), args[0]), window
        )
        
class EditPreferenceContextualCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        view = window.activeView()
        pkgDir = os.path.split(os.path.split(view.options().get('syntax'))[0])[1]
        
        if args[0] == 'shortcutKeys':
            f = 'Default.sublime-keymap'
        
        elif args[0] == 'preferences':
            f = '%s.sublime-options' % pkgDir
        
        openPreference(
            os.path.normpath(os.path.join(sublime.packagesPath(), pkgDir, f)),
            window
        )

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