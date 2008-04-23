from __future__ import with_statement

import sublime, sublimeplugin, os, sys, re

def openPreference(f, window):
    if not os.path.exists(f):
        with open(f, 'w') as fh:
            if f.endswith('sublime-keymap'):
                fh.write("<bindings>\n</bindings>")
            else:                
                fh.write("File did not exist: creating")
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