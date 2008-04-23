from __future__ import with_statement

import sublime, sublimeplugin, os, sys, re

class EditPreferenceCommand(sublimeplugin.WindowCommand):
    
    def run(self, window, args):
        print args
        window.openFile(os.path.join(sublime.packagesPath(), args[0]))


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