###############################################################################

# Std Libs
import os
import re
import string
import time

from os.path import join, normpath, dirname, abspath
from itertools import takewhile, groupby
from operator import itemgetter as iget

# Sublime Libs
import sublime
import sublimeplugin

# User Libs
import ctags

###############################################################################

def walkUpDirAndFindFile(file):
    dirs = normpath(file).split(os.path.sep)
    f = dirs.pop()
    
    while dirs:
        joined = normpath(os.path.sep.join(dirs + [f]))
        if os.path.exists(joined): return joined
        else: dirs.pop()

###############################################################################

ctags_cache    =   ctags.CTagsCache()

class NavigateToDefinitionCommand(sublimeplugin.TextCommand):
    events   =   {}
    tags     =   {}

    def onActivated(self, view):
        if not self.events or view.isLoading(): return

        fn = view.fileName()
        if fn: fn = os.path.normpath(fn)
        if fn not in self.events: return

        found_tag = view.find(self.events.pop(fn), 0, sublime.LITERAL)
        if found_tag:
            sel_set = view.sel()
            sel_set.clear()
            sel_set.add(found_tag)
            view.show(found_tag)

    def jump(self, view, tag_file, ex_command):
        tag_file = normpath(join(self.tag_dir, tag_file))
        window = view.window()

        if ex_command.isdigit():
            window.openFile(tag_file, int(ex_command), 1)
        else:
            self.events[tag_file] = ex_command
            window.openFile(tag_file)

    def quickOpen(self, view, files, disp):
        window = view.window()
        window.showQuickPanel("", "navigateToDefinition", files, disp)

    def run(self, view, args):
        if args:
            self.jump(view, *eval(args[0]))            
            return

        tags_file = walkUpDirAndFindFile (
            join(dirname(view.fileName() or '.'), 'tags') )
        if not tags_file:
            return

        current_symbol = view.substr(view.word(view.sel()[0]))
        self.tag_dir = dirname(tags_file)

        tags = ctags_cache.get(tags_file)
        if not tags: 
            return sublime.statusMessage('Parsing Ctags File')

        tags = [(t['filename'], t['ex_command']) for t in tags[current_symbol]]
        tags = sorted(tags)

        if len(tags) > 1:
            display =  ['%s : %s' % (i[0], `i[1]`) for i in tags]
            self.quickOpen(view, [`t` for t in  tags], display)

        elif tags: 
            self.jump(view, *tags[0])

################################################################################