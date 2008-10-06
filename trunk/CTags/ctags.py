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
import parse_ctags

###############################################################################

def walkUpDirAndFindFile(file):
    dirs = normpath(file).split(os.path.sep)
    f = dirs.pop()
    
    while dirs:
        joined = normpath(os.path.sep.join(dirs + [f]))
        if os.path.exists(joined): return joined
        else: dirs.pop()

###############################################################################

class NavigateToDefinitionCommand(sublimeplugin.TextCommand):
    events   =   {}
    tags     =   {}
    cache    =   {}
        
    def onActivated(self, view):
        if not self.events or view.isLoading(): return

        fn = view.fileName()
        if fn: fn = os.path.normpath(fn)
        if fn not in events: return

        found_tag = view.find(events.pop(fn), 0, sublime.LITERAL)
        if found_tag:
            sel_set = view.sel()
            sel_set.clear()
            sel_set.add(found_tag)
            view.show(found_tag)

    def jump(self, view, tag_file):
        # TODO: if there is more than one tag per symbol/file
        #       open a quickPanel to choose which symbol to go to in the
        #       current file
        
        ex_command = self.tags[tag_file][0]

        tag_file = normpath(join(self.tag_dir, tag_file))
        window = view.window()

        if ex_command.isdigit():
            window.openFile(tag_file, int(ex_command), 1)
        else:
            self.events[tag_file] = ex_command
            window.openFile(tag_file)

    def quickOpen(self, view, files):
        window = view.window()
        window.showQuickPanel("", "navigateToDefinition", files)

    def run(self, view, args):
        if args:
            return self.jump(view, args[0])

        tags_file = walkUpDirAndFindFile(join(dirname(view.fileName()), 'tags'))
        if not tags_file:
            return

        current_symbol = view.substr(view.word(view.sel()[0]))
        self.tag_dir = dirname(tags_file)

        while tags_file not in self.cache:
            self.cache[tags_file] = parse_ctags.parse_tag_file(tags_file)

        tags = self.cache[tags_file]

        self.tags = dict (
            (f, [t['ex_command'] for t in v]) for (f, v) in
            groupby(tags.get(current_symbol, []), iget('filename')) 
        )

        if len(self.tags) > 1:     self.quickOpen(view, self.tags.keys())
        elif self.tags:            self.jump(view, self.tags.keys()[0])

################################################################################