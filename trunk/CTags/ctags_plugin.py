#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

from __future__ import with_statement

# Std Libs
import os
import re
import time
import functools
import string
import pprint
import glob

from os.path import join, normpath, dirname
from operator import itemgetter as iget

from itertools import chain

################################ SUBLIME IMPORTS ###############################

# Sublime Libs
import sublime
import sublimeplugin

from sublime import statusMessage

################################# AAA* IMPORTS #################################

# Helpers
from pluginhelpers import threaded, in_main, wait_until_loaded, select, on_idle

# AutoComplete
from autocomplete import register_autocomplete

# QuickPanel formatting
from quickpanelcols import format_for_display

################################## APP IMPORTS #################################

# Ctags
import ctags
from ctags import ( TagFile, SYMBOL, FILENAME, parse_tag_lines, Tag,
                    MATCHES_STARTWITH, PATH_ORDER )

################################### SETTINGS ###################################

CTAGS_EXE = join(sublime.packagesPath(), 'CTags', 'ctags.exe')

CTAGS_CMD = [CTAGS_EXE, '-R']

TAGS_PATHS = {
    'source.python' :  r'C:\Python25\Lib\tags',
}

# Create a local_settings.py, (don't version control ) and shadow any of
# the settings above

try:                   from local_settings import *
except ImportError:    pass

################################### CONSTANTS ##################################

OBJECT_PUNCTUATORS = {
    'class'    :  '.',
    'struct'   :  '::',
    'function' :  '/',
}

ENTITY_SCOPE = "entity.name.function, entity.name.type, meta.toc-list"

#################################### HELPERS ###################################

def view_fn(v): return v.fileName() or '.'

def find_tags_relative_to(view, ask_to_build=True):
    fn = view.fileName()
    if not fn: return ''

    dirs = normpath(join(dirname(fn), 'tags')).split(os.path.sep)
    f = dirs.pop()

    while dirs:
        joined = normpath(os.path.sep.join(dirs + [f]))
        if os.path.exists(joined): return joined
        else: dirs.pop()

    if ask_to_build:
        statusMessage("Can't find any relevant tags file")
        view.runCommand('rebuildCTags')

def alternate_tags_paths(view, tags_file):
    tags_paths = '%s_search_paths' % tags_file
    search_paths = [tags_file]

    if os.path.exists(tags_paths):
        search_paths.extend(open(tags_paths).read().split('\n'))

    for selector, path in TAGS_PATHS.items():
        if view.matchSelector(view.sel()[0].begin(), selector):
            search_paths.append(path)

    return filter(os.path.exists, search_paths)

################################# SCROLL TO TAG ################################

def follow_tag_path(view, tag_path, pattern):
    regions = [sublime.Region(0, 0)]

    for p in list(tag_path)[1:-1]:
        while True:                               #.end() is BUG!
            regions.append(view.find(p, regions[-1].begin(), sublime.LITERAL))
            if ( regions[-1] is None or (regions[-1] == regions[-2]) or
                 view.matchSelector(regions[-1].begin(), ENTITY_SCOPE) ):
                regions = [r for r in regions if r is not None]
                break

    start_at = max(regions, key=lambda r: r.begin()).begin() -1
    pattern_region = view.find(pattern, start_at, sublime.LITERAL)
    # print map(view.substr, regions)

    return pattern_region.begin()-1 if pattern_region else start_at

def scroll_to_tag(view, tag, hook=None):
    @wait_until_loaded(join(tag.root_dir, tag.filename))
    def and_then(view):
        look_from = None
        if tag.ex_command.isdigit():
            look_from = view.textPoint(int(tag.ex_command)-1, 0)
        else:
            look_from = follow_tag_path(view, tag.tag_path, tag.ex_command)

        if look_from is not None:
            symbol_region = view.find(tag.symbol, look_from, sublime.LITERAL)
            if symbol_region: select(view, symbol_region)
            # else: print 'no symbol region'

        if hook: hook(view)

############################## FORMATTING HELPERS ##############################

def format_tag_for_quickopen(tag, file=1):
    format = []
    tag = ctags.Tag(tag)

    if file: format.append(tag.filename )

    f=''
    for field in getattr(tag, "field_keys", []):
        if field in PATH_ORDER:
            punct = OBJECT_PUNCTUATORS.get(field, ' -> ')
            f += string.Template (
                '    %($field)s$punct%(symbol)s' ).substitute(locals())

    return format + [(f or tag.symbol) % tag, tag.ex_command]

def prepared_4_quickpanel(formatter=format_tag_for_quickopen, path_cols=()):
    def compile_lists(sorter):
        args, display = [], []

        for t in sorter():
            display.append(formatter(t))
            args.append(t)

        return args, format_for_display(display, paths=path_cols)

    return compile_lists

############################ FILE COLLECTION HELPERS ###########################

def tagged_project_files(view, tag_dir):
    window = view.window()
    if not window: return []
    project = window.project()
    fn = view_fn(view)

    if not project or ( project and
                        not  fn.startswith(dirname(project.fileName())) ):
        prefix_arg = fn
        files = glob.glob(join(dirname(fn),"*"))
    else:
        prefix_arg = project.fileName()
        mount_points = project.mountPoints()
        files = list( chain(*(d['files'] for d in mount_points)) )

    common_prefix = os.path.commonprefix([tag_dir, prefix_arg])
    return [fn[len(common_prefix)+1:] for fn in files]

def files_to_search(view, tags_file, multiple=True):
    fn = view.fileName()
    if not fn: return

    tag_dir = normpath(dirname(tags_file))

    common_prefix = os.path.commonprefix([tag_dir, fn])
    files = [fn[len(common_prefix)+1:]]

    if multiple:
        more_files = tagged_project_files(view, tag_dir)
        files.extend(more_files)

    return files

############################### JUMPBACK COMMANDS ##############################

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

            del JumpBack.mods[:i]
            if not in_different_mod_area:
                jf, jr = f, region
  
        if in_different_mod_area or not JumpBack.mods:
            JumpBack.mods.insert(0, (jf, `jr`))
 
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
        sel = view.sel()
        if len(sel):
            JumpBack.mods.insert(0, (view.fileName(), `sel[0]`))
            del JumpBack.mods[100:]

################################ CTAGS COMMANDS ################################

def ctags_goto_command(jump_directly_if_one=False):
    def wrapper(f):
        def command(self, view, args):
            tags_file = find_tags_relative_to(view)

            result = f(self, view, args, tags_file, {})

            if result not in (True, False, None):
                args, display = result

                def on_select(i):
                    JumpBack.append(view)
                    scroll_to_tag(view, args[i])

                ( on_select(0) if   jump_directly_if_one and len(args) == 1
                               else view.window().showSelectPanel (
                                                  display, on_select, None, 0) )
        return command
    return wrapper

def checkIfBuilding(self, view, args):
    if RebuildCTags.build_ctags.func.running:
        statusMessage('Please wait while tags are built')

    else:  return 1

######################### GOTO DEFINITION UNDER CURSOR #########################

class NavigateToDefinition(sublimeplugin.TextCommand):
    isEnabled = checkIfBuilding

    @ctags_goto_command(jump_directly_if_one=True)
    def run(self, view, args, tags_file, tags):
        symbol = view.substr(view.word(view.sel()[0]))

        for tags_file in alternate_tags_paths(view, tags_file):
            tags = TagFile(tags_file, SYMBOL).get_tags_dict(symbol)
            if tags: break

        if not tags:
            return statusMessage('Can\'t find "%s"' % symbol)

        @prepared_4_quickpanel()
        def sorted_tags():
            return sorted(tags.get(symbol, []), key=iget('tag_path'))

        return sorted_tags

################################# SHOW SYMBOLS #################################

class ShowSymbols(sublimeplugin.TextCommand):
    isEnabled = checkIfBuilding

    @ctags_goto_command()
    def run(self, view, args, tags_file, tags):
        files = files_to_search(view, tags_file, 'multi' in args)
        if not files: return

        tags_file = tags_file + '_sorted_by_file'
        tags = TagFile(tags_file, FILENAME).get_tags_dict(*files)
        
        if not tags:
            return (
             'multi' in args and view.runCommand('showSymbols', ['multi'])
                     or sublime.questionBox (
                        'No symbols found **FOR CURRENT FILE**; Try Rebuild?' )
                    and view.runCommand('rebuildCTags') )

        path_cols = (0,) if len(files) > 1 else ()
        formatting = functools.partial( format_tag_for_quickopen,
                                        file = bool(path_cols)  )

        @prepared_4_quickpanel(formatting, path_cols=path_cols)
        def sorted_tags():
            return sorted (
                chain(*(tags[k] for k in tags)), key=iget('tag_path'))
                
        return sorted_tags

################################# REBUILD CTAGS ################################

class RebuildCTags(sublimeplugin.TextCommand):
    def run(self, view, args):
        tag_file = find_tags_relative_to(view, ask_to_build=0)
        if not tag_file:
            tag_file = join(dirname(view_fn(view)), 'tags')
            if not sublime.questionBox('`ctags -R` in %s ?'% dirname(tag_file)):
                return

        self.build_ctags(tag_file)

    def done_building(self, tag_file):
        statusMessage('Finished building %s' % tag_file)

    @threaded(finish=done_building, msg="Already running CTags!")
    def build_ctags(self, tag_file):
        in_main(lambda: statusMessage('Re/Building CTags: Please be patient'))()
        ctags.build_ctags(CTAGS_CMD, tag_file)
        return tag_file

################################# AUTOCOMPLETE #################################

@register_autocomplete()
def ctags_completion(view, prefix, cursor_pt):
    tags = find_tags_relative_to(view, ask_to_build=False)
    if tags:
        tag_file = TagFile(tags, SYMBOL, MATCHES_STARTWITH)
        return tag_file.get_tags_dict(prefix)

##################################### TEST #####################################

class TestCTags(sublimeplugin.TextCommand):
    routine = None

    def run(self, view, args):
        if self.routine is None:
            self.routine = self.co_routine(view)
            self.routine.next()

    def next(self):
        try:
            self.routine.next()
        except Exception, e:
            self.routine = None

    def co_routine(self, view, *args):
        tag_file = join(dirname(CTAGS_EXE), 'tags')
        with open(tag_file) as tf:
            tags = parse_tag_lines(tf, tag_class=Tag)

        print 'Starting Test'

        ex_failures = []
        line_failures = []

        for symbol, tag_list in tags.items():
            for tag in tag_list:
                tag.root_dir = dirname(tag_file)

                def hook(av):
                    if not av.substr(av.line(av.sel()[0])) == tag.ex_command:
                        failure = 'FAILURE %s' %pprint.pformat(tag)
                        failure += av.fileName()
                        sublime.messageBox('%s\n\n\n' % failure)
                        ex_failures.append(tag)
 
                    if tag.get('line'):
                        line = view.rowcol(av.sel()[0].begin())[0]+1
                        tag_line = int(tag.line)

                        if not tag_line == line:
                            line_failures.append((line, abs(line-tag_line), tag))

                    sublime.setTimeout( self.next, 1 )

                scroll_to_tag(view, tag, hook)
                yield

        failures = line_failures + ex_failures
        tags_tested = sum(len(v) for v in tags.values()) - len(failures)

        sublime.messageBox('%s Tags Tested OK' % tags_tested)
        sublime.messageBox('%s Tags Failed'    % len(failures))

        sublime.setClipboard(pprint.pformat(failures))

################################################################################