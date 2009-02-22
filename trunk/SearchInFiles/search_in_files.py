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

from itertools import chain
from os.path import dirname, split, join, splitext, normpath

# Sublime Modules

import sublime
import sublimeplugin

# User Libs
from plugin_helpers import wait_until_loaded, view_fn, threaded

################################### SETTINGS ###################################

choose_files_to_search = 0
open_new_window = 1

re_compile_flags = re.M

print_debug = 1

################################################################################


CONSTANTS = (NEXT, STOP_SEARCH) = (['NEXT'], ['STOP_SEARCH'])

regex_syntax = "Packages/Regular Expressions/RegExp.tmLanguage"

PANEL_SYNTAXES = [
    "Packages/Text/Plain text.tmLanguage",
    regex_syntax,
]

def is_regex_search(view):
    return view.options().get('syntax') == regex_syntax

################################################################################

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
    # Is the `view` a reference to the find panel?
    syntax = view.options().get('syntax')
    active_view = sublime.activeWindow().activeView()

    return (
        # in case of untitled view, `None != None`
            syntax in PANEL_SYNTAXES and
            view.fileName() != active_view.fileName() or
            view.size() != active_view.size() or
            tuple_regions(view) != tuple_regions(active_view)
        )

def full_buffer(view):
    return view.substr(sublime.Region(0, view.size()))

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
        enabled = args or view_is_find_panel(view)
        if not enabled:
            show_find_panel()
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
                # self.routine = None
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
        
        if choose_files_to_search:
            self.quick_panel (files_to_search, files=1, safe=0 )
            files_to_search = (yield)

        self.search(files_to_search, full_buffer(view), is_regex_search(view))
        add_jumpback()

        finds = map(eval, (yield))
        self.quick_panel ( [f[1] for f in finds], files=1,
                           display=['(%3s) %s' % f for f in finds] )

        finds = (yield)

        if open_new_window and len(finds) > 1:
            self.NEXT()
            yield sublime.runCommand('newWindow')

        @timeout
        def later():
            for f in finds:
                @wait_until_loaded(f)
                def and_then(view):
                    view.window().runCommand('findAll')

    def NEXT(self):
        self.run_self(NEXT)

    def run_self(self, args=[]):
        @timeout
        def later():
            sublime.activeWindow().activeView().runCommand('findInFiles', args)

    def finish(self, results):
        sublime.activeWindow().runCommand('hidePanel')
        
        finds, errors = results
        if not finds:
            return sublime.setTimeout (
                functools.partial(sublime.statusMessage, 'Found no files'), 100
            )

        results = 'Finds:\n%s\nErrors:\n%s' % \
                   tuple(map(pprint.pformat, [finds, errors]))

        sublime.setClipboard(results)

        @timeout
        def notify():
            'Else msgs from thread will drown it out'
            if errors:
                sublime.messageBox( 'Files couldn\'t be searched: \n\n%s' %
                                     '\n'.join(errors) )
            sublime.statusMessage("Results are on clipboard as python list")

        sublime.activeWindow().activeView().runCommand('findInFiles', 
            map(repr, finds))

################################################################################

    @threaded(finish=finish, msg='search already running')
    def search(self, files, pattern, is_regex):
        findings = []
        errors = []

        if not is_regex: pattern = re.escape(pattern)
        matcher = re.compile(pattern, re.M)
        num_files = len(files)
        self.stop_search = 0

        def search(search_in):
            matches = matcher.findall(search_in)
            if matches:
                findings.append((len(matches), f))

        for i, f in enumerate(files):
            if self.stop_search:
                break
                sublime.statusMessage('search cancelled')

            @timeout
            def status():
                sublime.statusMessage(" (%s of %s) ctrl+shift+z to cancel %s"
                                        % (i+1, num_files, f) )
            try:
                with open(f, 'r+') as fh:
                    search(mmap.mmap(fh.fileno(), 0))
                    
            except Exception, e:
                try:
                    with open(f) as fh:
                        search(fh.read())

                except Exception, e:
                    errors.append((f, `e`))

        return sorted(findings, reverse=True), errors

class EscapeRegex(sublimeplugin.TextCommand):
    def run(self, view, args):
        for sel in view.sel():
            view.replace(sel, re.escape(view.substr(sel)))

################################################################################