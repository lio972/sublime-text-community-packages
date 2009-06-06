################################################################################
# Std Libs
from __future__ import with_statement

import re
import os
import functools
import time
import glob
import mmap
import threading
import pprint
import datetime
from ctypes import windll

from itertools import chain, count
from os.path import dirname, split, join, splitext, normpath as norm
from datetime import datetime

# Sublime Modules
import sublime
import sublimeplugin

# User Libs
from plugin_helpers import wait_until_loaded, view_fn, threaded

from cache import SearchResultsCache
from render_results import render_and_dump

################################### SETTINGS ###################################

FIND_PANEL_VIEW_ID = 3
CHOOSE_FILES_TO_SEARCH = 0
OPEN_NEW_WINDOW = 0
RE_COMPILE_FLAGS = re.M

OPEN_HTML_SUBLIME_PROTOCOL = 1

try:
    from local_settings import *
except ImportError:
    pass

################################################################################

CONSTANTS = (NEXT, STOP_SEARCH) = (['NEXT'], ['STOP_SEARCH'])

REGEX_SYNTAX = "Packages/Regular Expressions/RegExp.tmLanguage"
TEXT_SYNTAX  = "Packages/Text/Plain text.tmLanguage"

PANEL_SYNTAXES = (TEXT_SYNTAX, REGEX_SYNTAX)


RE_SPECIAL_CHARS = re.compile (
    '(\\\\|\\*|\\+|\\?|\\||\\{|\\[|\\(|\\)|\\^|\\$|\\.|\\#|\\ )' )

################################################################################

class FocusRestorer(object):
    def __init__(self): 
        self.h = windll.user32.GetForegroundWindow()
    def __call__(self, times=2, delay = 50):  
        for t in xrange(1, (delay * times) + 2, delay):
            sublime.setTimeout (
                functools.partial(windll.user32.SetForegroundWindow, self.h), t
            )

def is_regex_search(view):
    return view.options().get('syntax') == REGEX_SYNTAX

def escape_regex(s):
    return RE_SPECIAL_CHARS.sub(lambda m: '\\%s' % m.group(1), s)

def do_in(t=0):
    def timeout(f):
        return sublime.setTimeout(f, t)
    return timeout

def timeout(f):
    return sublime.setTimeout(f, 10)

def add_jumpback():
    try:
        ( sublimeplugin.allCommands[1]['jumpBack'].append(sublime.activeWindow()
                                                  .activeView()))
    except Exception, e:
        pass

def show_find_panel():
    window = sublime.activeWindow()
    window.runCommand('hidePanel')
    window.runCommand('showPanel find')

def tuple_regions(view):
    return tuple((r.begin(), r.end()) for r in view.sel())

def view_is_find_panel(view):
    aw = sublime.activeWindow()
    return (
        ( aw.id() == 1 and view.id() == FIND_PANEL_VIEW_ID) or
         (aw.id() != 1 and view.id() not in [v.id() for v in aw.views()] )
    )

def full_buffer(view):
    return view.substr(sublime.Region(0, view.size()))

################################# CACHED SEARCH ################################

CACHE = SearchResultsCache()

def clean_up(cache):
    now = datetime.now()
    have_lock = cache.lock.acquire(0)

    if have_lock:
        try:
            for key in list(cache):
                delta = now - cache[key]['cached_at']

                if delta.seconds > MAX_AGE:
                    del cache[key]                
        finally:
            cache.lock.release()

    sublime.setTimeout(lambda: clean_up(cache), 1000 * 60 * 10)

clean_up(CACHE)

def cached_search(f, pattern, matcher):
    aw = sublime.activeWindow()
    
    # Check open dirty files using view findAll api 
    for v in aw.views():
        if norm(v.fileName() or '') == norm(f) and v.isDirty():
            found = len(v.findAll(pattern))
            return ((found, f) if found else None, None)

    def do_search():
        def search(search_in):
            matches = [0 for i in matcher.finditer(search_in)]
            if matches:
                return (len(matches), f)

        # MMAP
        try:
            with open(f, 'r+') as fh:
                return search(mmap.mmap(fh.fileno(), 0)), None

        # Normal File Open
        except Exception, e:
            try:
                with open(f) as fh:
                    return search(fh.read()), None

            except Exception, e:
                return None, (f, `e`)

    return CACHE.get((f, pattern), do_search)

################################# MESSAGE QUEUE ################################

def send_message(msg):
    sublime.setTimeout(lambda: sublime.statusMessage(msg), 10)

################################################################################

class FindInFiles(sublimeplugin.TextCommand):
    routine = None

    def quick_panel(self, args, files=False, display=None, safe=True):
        flags = sublime.QUICK_PANEL_MULTI_SELECT
        if files:
            flags = flags | sublime.QUICK_PANEL_FILES
        if not safe:
            flags = flags | sublime.QUICK_PANEL_NO_MULTI_SELECT_SAFETY_CHECK

        sublime.activeWindow().showQuickPanel ( '','findInFiles',
                                                args, display or args, flags )

    def isEnabled(self, view, args):
        if self.search.running: return False

        is_find_panel = view_is_find_panel(view)

        enabled = args or is_find_panel
        if not enabled:
            show_find_panel()
            self.routine = None

        # Reset the command if in find panel with no args and routine already 
        # started
        elif is_find_panel and not args and self.routine:
            self.routine = None

        return enabled

    def run(self, view, args):
        if self.routine is None:
            self.routine = self.co_routine(view, args)
            self.routine.next()

        try:
            if args == NEXT:
                self.routine.next()
            elif args == STOP_SEARCH:
                self.stop_search = True
            else:
                self.routine.send(args)

        except Exception, e:
            self.routine = None

    def co_routine(self, view, args):
        yield

        window = sublime.activeWindow()
        mount_points = window.project().mountPoints()
        mount_paths = [d['path'] for d in mount_points]

        if len(mount_paths) > 1:
            self.quick_panel(mount_paths)
            mount_paths = (yield)
            mount_points = [d for d in mount_points if d['path'] in mount_paths]

        files_to_search = list( chain(*(d['files'] for d in mount_points)) )

        if CHOOSE_FILES_TO_SEARCH:
            self.quick_panel (files_to_search, files=1, safe=0 )
            files_to_search = (yield)
        
        self.pattern = full_buffer(view)
        self.restore = FocusRestorer()
        
        self.search(files_to_search, self.pattern, is_regex_search(view))
        add_jumpback()

        finds = map(eval, (yield))
        self.quick_panel ( [f[1] for f in finds], files=1,
                           display=['(%3s) %s' % f for f in finds] )

        finds = (yield)

        if OPEN_NEW_WINDOW and len(finds) > 1:
            self.NEXT()
            yield sublime.runCommand('newWindow')

        @timeout
        def later():
            for f in finds:
                @wait_until_loaded(f)
                def and_then(view):
                    sublime.activeWindow().focusView(view)
                    sublime.activeWindow().runCommand('findAll')

    def NEXT(self):
        self.run_self(NEXT)

    def run_self(self, args=[]):
        @timeout
        def later():
            sublime.activeWindow().activeView().runCommand('findInFiles', args)

    def finish(self, finds, errors):
        if not finds:
            return sublime.setTimeout (
                functools.partial(sublime.statusMessage, 'Found no files'), 100
            )

        results = pprint.pformat({'finds':finds, 'errors':errors})
        sublime.setClipboard(results)
        
        if OPEN_HTML_SUBLIME_PROTOCOL:
            render_and_dump(findings=finds, pattern=self.pattern)
            self.restore()
        
        @timeout
        def notify():
            'Else msgs from thread will drown it out'
            if errors:
                sublime.messageBox( 'Files couldn\'t be searched: \n\n%s' %
                                     '\n'.join(errors) )
            sublime.statusMessage("Results are on clipboard as python dict")

        sublime.activeWindow().activeView().runCommand('findInFiles', 
            map(repr, finds))

################################################################################

    @threaded(finish=finish, msg='search already running')
    def search(self, files, pattern, is_regex):
        findings = []
        errors = []

        if not is_regex: pattern = escape_regex(pattern)
        matcher = re.compile(pattern, RE_COMPILE_FLAGS)
        num_files = len(files)
        self.stop_search = 0

        with CACHE.lock:
            for i, f in enumerate(files):
                if self.stop_search:
                    break

                t = time.time()

                found, error  = cached_search(f, pattern, matcher)

                if (time.time() - t) > 0.03 or (i % 20 == 0):
                    send_message(" (%s of %s) ctrl+shift+z to stop %s"
                            % (i+1, num_files, f) )
    
                if found:    findings.append(found)
                if error:    errors.append(error)

            return sorted(findings, reverse=True), errors

class EscapeRegex(sublimeplugin.TextCommand):
    def run(self, view, args):
        for sel in view.sel():
            view.replace(sel, escape_regex(view.substr(sel)))

################################################################################