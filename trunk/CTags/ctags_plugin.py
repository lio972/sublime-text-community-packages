################################################################################

# Std Libs
import os
import re
import string
import time
import threading
import functools

from os.path import join, normpath, dirname, abspath
from itertools import takewhile, groupby
from operator import itemgetter as iget

# Sublime Libs
import sublime
import sublimeplugin

# User Libs
import ctags

################################################################################

def find_tags_relative_to(view):
    fn = view.fileName()
    if not fn: return
    
    dirs = normpath(join(dirname(fn), 'tags')).split(os.path.sep)
    f = dirs.pop()
    
    while dirs:
        joined = normpath(os.path.sep.join(dirs + [f]))
        if os.path.exists(joined): return joined
        else: dirs.pop()

def view_fn(view, if_None = '.'):
    return normpath(view.fileName() or if_None)
    
def wait_until_loaded(file, window):
    window.openFile(file)
    v = [v for v in window.views() if view_fn(v) ==  normpath(file)][0]

    if not v.isLoading(): return lambda f: f(v)

    def wrapper(f):
        def wait():
            while v.isLoading():
                time.sleep(0.01)
            sublime.setTimeout(functools.partial(f, v), 0)
        t = threading.Thread(target=wait)
        return t.start()
    return wrapper

def select(view, region):
    sel_set = view.sel()
    sel_set.clear()
    sel_set.add(region)
    view.show(region)    

def scroll_to_tag(view, file, symbol, pattern_or_line):

    @wait_until_loaded(file, view.window())
    def and_then(view):
        look_from = None
        if pattern_or_line.isdigit():
            look_from = view.textPoint(int(pattern_or_line)-1, 0)
        else:
            found_tag = view.find(pattern_or_line, 0, sublime.LITERAL)
            if found_tag: look_from = found_tag.begin()

        if look_from is not None:
            symbol_region = view.find(symbol, look_from, sublime.LITERAL)
            select(view, symbol_region)

def format_tag_for_quickopen(tag):
    if 'class' in tag: format = "%(filename)s : %(class)s %(ex_command)s" 
    else:              format = "%(filename)s : %(ex_command)s" 
    
    return format % tag

################################################################################

ctags_cache    =   ctags.CTagsCache()

################################################################################

class ShowSymbolsForCurrentFile(sublimeplugin.TextCommand):
    def run(self, view, args):
        if args:
            view = self.view
            scroll_to_tag(view, view.fileName(), *eval(args[0]))
            del self.view
            return
        
        tags_file = find_tags_relative_to(view)
        if not tags_file: return
                
        fn = view_fn(view, None) 
        if not fn: return
        
        tag_dir = normpath(dirname(tags_file))
        common_prefix = os.path.commonprefix([tag_dir, fn])
        current_file = intern(fn[len(common_prefix)+1:].encode('utf-8'))

        tags = ctags_cache.get(tags_file)
        if not tags:
            return sublime.statusMessage('Parsing Ctags File')
        
        tags_for_current_file = []
        
        for symbol, tag_list in tags.iteritems():
            for t in tag_list:
                if t['filename'] == current_file:
                    tags_for_current_file += [t]
 
        args, display = [], []
        
        for t in sorted(tags_for_current_file, key=iget('symbol')):
            args    += [`(t['symbol'], t['ex_command'])`]
            display += [format_tag_for_quickopen(t)]

        self.view = view

        window = view.window()
        window.showQuickPanel('', 'showSymbolsForCurrentFile', args, display)

################################################################################

class NavigateToDefinitionCommand(sublimeplugin.TextCommand):
    last_open = None
    
    def jump(self, view, args):
        scroll_to_tag(view, *args)

    def jumpBack(self):
        if self.last_open:
            self.window.focusView(self.last_open)
            select(self.last_open, self.selection)

    def quickOpen(self, view, files, disp):
        window = view.window()
        window.showQuickPanel("", "navigateToDefinition", files, disp)

    def run(self, view, args):
        if args:
            if args[0] == 'jumpBack': return self.jumpBack()
            else: return self.jump(view, eval(args[0]))
        
        tags_file = find_tags_relative_to(view)
        if not tags_file: return

        current_symbol = view.substr(view.word(view.sel()[0]))
        tag_dir = dirname(tags_file)

        tags = ctags_cache.get(tags_file)
        if not tags: return sublime.statusMessage('Parsing Ctags File')
                
        args, display = [], []
        for t in sorted(tags.get(current_symbol, []), key=iget('filename')):
            args    += [
                (join(tag_dir,t['filename']), t['symbol'], t['ex_command']) ] 
            
            display += [format_tag_for_quickopen(t)]

        self.last_open = view
        self.window = view.window()
        self.selection = view.sel()[0]

        if len(args) > 1:
            self.quickOpen(view, [`t` for t in  args],  display)

        elif args:
            self.jump(view, args[0])

################################################################################