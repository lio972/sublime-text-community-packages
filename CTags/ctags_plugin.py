################################################################################

# Std Libs
import os
import re
import time
import threading
import functools
import subprocess

from os.path import join, normpath, dirname, abspath, basename
from operator import itemgetter as iget

from itertools import chain, groupby

# Sublime Libs
import sublime
import sublimeplugin
from sublime import statusMessage

# User Libs
import ctags

from ctags import TagFile, SYMBOL, FILENAME
from plugin_helpers import threaded, FocusRestorer, in_main

# from helpers import time_function

################################################################################

ctags_exe = join(sublime.packagesPath(), 'CTags', 'ctags.exe')

################################################################################

def find_tags_relative_to(view, ask_to_build=True):
    fn = view.fileName()
    if not fn: return
    
    dirs = normpath(join(dirname(fn), 'tags')).split(os.path.sep)
    f = dirs.pop()
    
    while dirs:
        joined = normpath(os.path.sep.join(dirs + [f]))
        if os.path.exists(joined): return joined
        else: dirs.pop()
    
    if ask_to_build:
        statusMessage("Can't find any relevant tags file")
        view.runCommand('rebuildCTags')

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

def follow_tag_path(view, tag_path, pattern):
    # path = map(re.escape, list(tag_path)[1:-1])
    # path = '(.|[\r\n])*?'.join('%s' % p for p in path + [re.escape(pattern)])
    
    # regions = []
    
    # start = 0
    
    # while True:
    #     regions.append(view.find(path, start, 0))
    #     if not regions[-1]: break
    #     else: start = regions[-1].end()

    # regions = sorted((t for t in regions if t), key=sublime.Region.size)
    # if regions: start = view.line(regions[0].end()).begin()
    
    # return view.find(pattern, start, sublime.LITERAL).begin()
    
    last_start = 0
        
    for p in list(tag_path)[1:-1] + [pattern]:
        while True:
            start = view.find(p, last_start, sublime.LITERAL)
            if not start: break

            if p == pattern:
                last_start = start.begin() -1
                break

            if start.begin() == last_start:  break

            last_start = start.begin() + 1
            is_func = view.matchSelector(last_start, 'entity')
            if is_func: break

    return view.line(last_start).begin()

def scroll_to_tag(view, tag_dir, tag):
    tag = ctags.Tag(tag)
 
    symbol, pattern_or_line = tag.symbol, tag.ex_command


    @wait_until_loaded(join(tag_dir, tag.filename), view.window())
    def and_then(view):
        
        look_from = None
        if pattern_or_line.isdigit():
            look_from = view.textPoint(int(pattern_or_line)-1, 0)
        else:
            look_from = follow_tag_path(view, tag.tag_path, pattern_or_line)

        if look_from is not None:
            symbol_region = view.find(symbol, look_from, sublime.LITERAL)
            select(view, symbol_region)

def format_tag_for_quickopen(tag, file=1):
    
    if file: format         = "%(filename)s:\t"
    else:    format         = ""
    
    if 'class' in tag: 
        format         += "\t%(class)s.%(symbol)s:\t" % tag

    elif 'struct' in tag: 
        format         += "\t%(struct)s::%(symbol)s:\t" % tag
        
    elif 'function' in tag:
        format         += "\t%(function)s/%(symbol)s:\t" % tag
    
    if not format: format = '%(symbol)s'
    
    s = format % tag
    space = (80 - len(s)) * ' ' 
    
    return    s + space + ("%(ex_command)s" % tag)

format_for_current_file = functools.partial(format_tag_for_quickopen, file=0)

################################################################################

def checkIfBuilding(self, view, args):
    if RebuildCTags.building:
        statusMessage('Please wait while tags are built')

    else:  return 1

################################################################################

def prepared_4_quickpanel(formatter=format_tag_for_quickopen):
    def compile_lists(sorter):
        args, display = [], []

        for t in sorter():
            display.append(formatter(t))
            args.append(t)
        return args, display

    return compile_lists

class ShowSymbolsForCurrentFile(sublimeplugin.TextCommand):
    isEnabled = checkIfBuilding
    
    # @time_function
    def run(self, view, args):
        tags_file = find_tags_relative_to(view)
        if not tags_file: return

        fn = view_fn(view, None)
        if not fn: return

        tag_dir = normpath(dirname(tags_file))
        common_prefix = os.path.commonprefix([tag_dir, fn])
        current_file = '.\\' + fn[len(common_prefix)+1:]

        ################################################################

        tags_file = tags_file + '_unsorted'
        tags = TagFile(tags_file, FILENAME).get_tags_dict(current_file)

        if tags:  JumpBack.append(view)
        
        @prepared_4_quickpanel(format_for_current_file)
        def sorted_tags():
            for t in sorted(chain(*(tags[k] for k in tags)), key=iget('tag_path')):
                yield t

        ################################################################
        
        (QuickPanel.partial(scroll_to_tag, view, tag_dir)
                   .show(*sorted_tags))
        
################################################################################

class QuickPanel(sublimeplugin.WindowCommand):
    def onActivated(self, view):
        QuickPanel.window = view.window()

    @classmethod
    def show(cls, args, display, skip_if_one=False):
        if skip_if_one and len(args) < 2: return cls.f(args[0])
        cls.args = args
        args = map(repr, range(len(args)))
        cls.window.showQuickPanel('', 'quickPanel', args, display)

    @classmethod
    def partial(cls, f, *args, **kw):
        cls.f = staticmethod(functools.partial(f, *args, **kw))
        return cls

    def run(self, window, args):
        arg = self.args[eval(args[0])]
        self.f(arg)
        del QuickPanel.f, QuickPanel.args

################################################################################

class JumpBack(sublimeplugin.WindowCommand):
    last = [(0, 0)]
    
    # @time_function
    def run(self, w, args):                    
        the_view, sel = JumpBack.last[-1]
        if len(JumpBack.last) > 1:  del JumpBack.last[-1]
  
        if not the_view: return statusMessage('JumpBack buffer empty')

        sel = sublime.Region(*eval(sel))
        
        if isinstance(the_view, unicode):
            @wait_until_loaded(the_view, w)
            def and_then(view):
                select(view, sel)

        else:
            w.focusView(the_view)
            select(the_view, sel)

    @classmethod
    def append(cls, view):
        fn = view.fileName()
        if fn:
            cls.last.append((fn, `view.sel()[0]`))
    
    def onModified(self, view):
        JumpBack.last[-1] = (view, `view.sel()[0]`)

################################################################################

class RebuildCTags(sublimeplugin.TextCommand):
    building = False

    def run(self, view, args):

        tag_file = find_tags_relative_to(view, ask_to_build=0)
        if not tag_file:
            tag_file = join(dirname(view_fn(view)), 'tags')
            if not sublime.questionBox('`ctags -R` in %s ?'% dirname(tag_file)):
                return
        
        RebuildCTags.building = True
        
        self.build_ctags(tag_file)
        statusMessage('Re/Building CTags: Please be patient')

    def done_building(self, tag_file):
        statusMessage('Finished building %s' % tag_file)
        RebuildCTags.building = False
    
    @threaded(finish=done_building, msg="Already running CTags")
    # @time_function
    def build_ctags(self, tag_file):
        ctags.build_ctags(ctags_exe, tag_file)
        return tag_file
        
################################################################################

class NavigateToDefinition(sublimeplugin.TextCommand):
    isEnabled = checkIfBuilding
    
    # @time_function
    def run(self, view, args):
        tags_file = find_tags_relative_to(view)
        if not tags_file: return
        
        symbol = view.substr(view.word(view.sel()[0]))
        tag_dir = dirname(tags_file)
        
        tags = TagFile(tags_file, SYMBOL).get_tags_dict(symbol)
        
        if not tags: 
            return statusMessage('Can\'t find "%s" in %s' % (symbol, tags_file))

        def sorted_tags():
            for t in sorted(tags.get(symbol, []), key=iget('tag_path')):
                yield t

        args, display = prepared_4_quickpanel()(sorted_tags)

        if args:
            JumpBack.append(view)
            (QuickPanel.partial(scroll_to_tag, view, tag_dir)
                       .show(args, display, skip_if_one = True))

################################################################################
"""

TODO:

Each command has this in common:

    Trys to find the tags relative to the view
    
    Finds the `field` to look for, eg symbol under cursor or filename
    
    Gets the tag_dir, dir housing relevant `tags` file
    
    Opens a TagFile, get a dictionary of of symbols
    
    Sorts all those dicts to the current commands specifications
    
    Creates `args and displays` for the quick panel for each Tag
    
    Appends to JumpBack the view
    
    Opens the QuickPanel
    
    
Ways to clean up the design:
    
    Less decorators and nested functions:
        Hard to test or debug

    Need a multisort (name ?):
        multisort(sequence, keys=(iget('filename'), iget('classname'))) * DONE *

"""
################################################################################
