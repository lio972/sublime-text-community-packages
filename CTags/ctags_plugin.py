################################################################################

# Std Libs
import os
import re
import time
import threading
import functools
import subprocess
import string
import pprint

from os.path import join, normpath, dirname
from operator import itemgetter as iget

from itertools import chain

# Sublime Libs
import sublime
import sublimeplugin
from sublime import statusMessage

# User Libs
import ctags

from ctags import TagFile, SYMBOL, FILENAME
from plugin_helpers import threaded, FocusRestorer, in_main

# NOTE

# This plugin relies on in_load.py to decorate sublimeplugin.onActivated

################################################################################

CTAGS_EXE = join(sublime.packagesPath(), 'CTags', 'ctags.exe')


# These are used for formatting tag paths for the QuickPanel

OBJECT_PUNCTUATORS = {
    'class'    :  '.',
    'struct'   :  '::',
    'function' :  '/',
}


ENTITY_SCOPE = "entity.name.function, entity.name.type, meta.toc-list"

################################################################################

def view_fn(view, if_None = '.'):
    return normpath(view.fileName() or if_None)

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

################################################################################

def follow_tag_path(view, tag_path, pattern):
    regions = [sublime.Region(0, 0)]

    for p in list(tag_path)[1:-1]:
        while True:
            regions.append(view.find(p, regions[-1].end(), sublime.LITERAL))
            if (not regions[-1] or (regions[-1] == regions[-2]) or
                view.matchSelector(regions[-1].begin(), ENTITY_SCOPE)):
                break

    regions = [r for r in regions if r is not None]
    start_at = max(regions, key=lambda r: r.begin()).begin()
    pattern_region = view.find(pattern, start_at, sublime.LITERAL)

    return pattern_region.begin() if pattern_region else start_at

def scroll_to_tag(view, tag_dir, tag):
    tag = ctags.Tag(tag)

    symbol, pattern_or_line = tag.symbol, tag.ex_command

    @wait_until_loaded(join(tag_dir, tag.filename))
    def and_then(view):
        look_from = None
        if pattern_or_line.isdigit():
            look_from = view.textPoint(int(pattern_or_line)-1, 0)
        else:
            look_from = follow_tag_path(view, tag.tag_path, pattern_or_line)

        if look_from is not None:
            symbol_region = view.find(symbol, look_from, sublime.LITERAL)
            select(view, symbol_region)

################################################################################

def format_tag_for_quickopen(tag, file=1):
    if file: format         = "%(filename)s:\t"
    else:    format         = ""

    for field in tag.get("field_keys", []):
        if field != "file":
            punct = OBJECT_PUNCTUATORS.get(field, ' -> ')
            format += string.Template (
                '    %($field)s$punct%(symbol)s' ).substitute(locals())

    if not format: format = '%(symbol)s'
    tag_info = (format % tag).rstrip()
    space    = (80 - len(tag_info)) * ' '

    return (tag_info + space + tag["ex_command"]).decode('utf8', 'ignore')

format_for_current_file = functools.partial(format_tag_for_quickopen, file=0)

################################################################################

def prepared_4_quickpanel(formatter=format_tag_for_quickopen):
    def compile_lists(sorter):
        args, display = [], []

        for t in sorter():
            display.append(formatter(t))
            args.append(t)
        return args, display

    return compile_lists

################################################################################

def checkIfBuilding(self, view, args):
    if RebuildCTags.building:
        statusMessage('Please wait while tags are built')

    else:  return 1

################################################################################

class ShowSymbolsForCurrentFile(sublimeplugin.TextCommand):
    isEnabled = checkIfBuilding

    def run(self, view, args):
        tags_file = find_tags_relative_to(view)
        if not tags_file: return

        fn = view_fn(view, None)
        if not fn: return

        tag_dir = normpath(dirname(tags_file))
        common_prefix = os.path.commonprefix([tag_dir, fn])
        current_file = fn[len(common_prefix)+1:]

        ################################################################

        tags_file = tags_file + '_sorted_by_file'
        tags = TagFile(tags_file, FILENAME).get_tags_dict(current_file)

        if tags:  JumpBack.append(view)

        @prepared_4_quickpanel(format_for_current_file)
        def sorted_tags():
            for t in sorted (
                chain(*(tags[k] for k in tags)), key=iget('tag_path')):
                yield t

        ################################################################

        (QuickPanel.partial(scroll_to_tag, view, tag_dir)
                   .show(*sorted_tags))

################################################################################

class QuickPanel(sublimeplugin.WindowCommand):
    @classmethod
    def show(cls, args, display, skip_if_one=False):
        if skip_if_one and len(args) < 2: return cls.f(args[0])
        cls.args = args
        args = map(repr, xrange(len(args)))
        sublime.activeWindow().showQuickPanel('', 'quickPanel', args, display)

    @classmethod
    def partial(cls, f, *args, **kw):
        cls.f = staticmethod(functools.partial(f, *args, **kw))
        return cls

    def run(self, window, args):
        arg = self.args[eval(args[0])]
        self.f(arg)
        del QuickPanel.f, QuickPanel.args

################################################################################

def different_mod_area(f1, f2, r1, r2):
    same_file   = f1 == f2
    same_region = abs(r1[0] - r2[0]) < 40
    return not same_file or not same_region

class JumpBack(sublimeplugin.WindowCommand):
    last    =     []
    mods    =     []

    def run(self, w, args):
        if 'toLastModification' in args:
            return self.lastModifications()

        if not JumpBack.last: return statusMessage('JumpBack buffer empty')

        f, sel = JumpBack.last.pop()
        self.jump(f, eval(sel))

    def lastModifications(self):
        # Current Region
        cv = sublime.activeWindow().activeView()
        cr = eval(`cv.sel()[0]`)
        cf   = cv.fileName()

        # Very latest, s)tarting modification
        sf, sr = JumpBack.mods.pop(0)
        sr = eval(sr)

        in_different_mod_area = different_mod_area (sf, cf, cr, sr)

        # Default J)ump F)ile and R)egion
        jf, jr = sf, sr

        if JumpBack.mods:
            for i, (f, r) in enumerate(JumpBack.mods):
                region = eval(r)
                if different_mod_area(sf, f, sr, region):
                    break

            del JumpBack.mods[:i+1]
            if not in_different_mod_area:
                jf, jr = f, region

        if not JumpBack.mods: JumpBack.mods.append((jf, `jr`))
        self.jump(jf, jr)

    def jump(self, fn, sel):
        @wait_until_loaded(fn)
        def and_then(view):
            select(view, sublime.Region(*sel))

    @classmethod
    def append(cls, view):
        fn = view.fileName()
        if fn:
            cls.last.append((fn, `view.sel()[0]`))

    def onModified(self, view):
        JumpBack.mods.insert(0, (view.fileName(), `view.sel()[0]`))
        del JumpBack.mods[100:]

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
    def build_ctags(self, tag_file):
        ctags.build_ctags(CTAGS_EXE, tag_file)
        return tag_file

################################################################################

class NavigateToDefinition(sublimeplugin.TextCommand):
    isEnabled = checkIfBuilding

    def run(self, view, args):
        tags_file = find_tags_relative_to(view)
        if not tags_file: return

        symbol = view.substr(view.word(view.sel()[0]))
        tag_dir = dirname(tags_file)
        tags = TagFile(tags_file, SYMBOL).get_tags_dict(symbol)

        if not tags:
            return statusMessage('Can\'t find "%s" in %s' % (symbol, tags_file))

        @prepared_4_quickpanel()
        def sorted_tags():
            for t in sorted(tags.get(symbol, []), key=iget('tag_path')):
                yield t

        args, display = sorted_tags

        if args:
            JumpBack.append(view)
            (QuickPanel.partial(scroll_to_tag, view, tag_dir)
                       .show(args, display, skip_if_one = True))

################################################################################