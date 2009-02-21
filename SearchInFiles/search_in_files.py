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

################################################################################

CONSTANTS = (NEXT,     STOP_SEARCH,     HIDE_PANEL) = (
           ['NEXT'], ['STOP_SEARCH'], ['HIDE_PANEL'] )

PANEL_SYNTAXES = [
    "Packages/Text/Plain text.tmLanguage",
    "Packages/Regular Expressions/RegExp.tmLanguage",
]

def is_regex_search(view):
    return PANEL_SYNTAXES.index(view.options().get('syntax'))

################################################################################

def do_in(t=0):
    def timeout(f):
        return sublime.setTimeout(f, t)
    return timeout

def timeout(f):
    return sublime.setTimeout(f, 0)

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
    searching = False

    def quick_panel(self, args, files=False, display=None, safe=True):
        flags = sublime.QUICK_PANEL_MULTI_SELECT
        if files:
            flags = flags | sublime.QUICK_PANEL_FILES
        if not safe:
            flags = flags | sublime.QUICK_PANEL_NO_MULTI_SELECT_SAFETY_CHECK

        sublime.activeWindow().showQuickPanel ( '','findInFiles',
                                                args, display or args, flags )

    def isEnabled(self, view, args):
        # If getting sent back args from quickpanel or in the find panel
        enabled = args or view_is_find_panel(view)

        if not self.searching and not enabled:
            # Kill the routine in case of command escaped out of  
            # early before generator was consumed

            show_find_panel()
            self.routine = None

        # Heuristic for determining whether selected from the async updated
        # findings panel. If so, must stop searching and hide overlay[s]
        # brought up by the timeouts set in the search thread

        if self.searching and args not in CONSTANTS:
            if args:
                self.stop_search = True
                w = view.window()
    
                @do_in(len(args) * 10)
                def shut_panel():
                    w.runCommand('hideOverlay')

            else:
                self.close_panel = False
                return False

        return enabled
    
    def reset(self, view, args):
        self.routine = self.co_routine(view, args)
        self.stop_search = False
        self.searching = False
        self.close_panel = False
        self.routine.next()
    
    def run(self, view, args):
        if self.routine is None:
            self.reset(view, args)
        try:
            if args == NEXT:
                self.routine.next()

            elif args == STOP_SEARCH:
                self.stop_search = True

            elif args == HIDE_PANEL:
                if self.searching:
                    self.close_panel = True
                
                @do_in(10)
                def l8r():
                    view.window().runCommand('hideOverlay')
                
            else:
                # stopped the search and pressed escape without finishing
                # co routine ( selecting a file sent through `args`)
                if not args and self.stop_search:
                    self.reset(view, args)

                self.routine.send(args)

        except StopIteration:
            self.reset(view, args)

    def co_routine(self, view, args):
        yield

        window = sublime.activeWindow()
        mount_points = window.project().mountPoints()
        mount_paths = [d['path'] for d in mount_points]

        if len(mount_paths) > 1:
            sublime.statusMessage('Pick mount[s] to search in')
            self.quick_panel(mount_paths)
            mount_points = [d for d in mount_points if d['path'] in (yield)]

        files_to_search = list( chain(*(d['files'] for d in mount_points)) )

        if choose_files_to_search:
            sublime.statusMessage('Pick file[s] to search in')
            self.quick_panel (files_to_search, files=1, safe=0 )
            files_to_search = (yield)

        self.searching = True
        self.search(
            files_to_search,  full_buffer(view), is_regex_search(view), window )

        add_jumpback()

        finds = (yield)
        if open_new_window and len(finds) > 1:
            self.NEXT()
            yield sublime.runCommand('newWindow')

        @do_in(10)
        def later():
            for f in finds:
                @wait_until_loaded(f)
                def and_then(view):
                    view.window().runCommand('findAll')

    def NEXT(self):
        self.run_self(NEXT)

    def run_self(self, args=[]):
        @do_in(10)
        def later():
            sublime.activeWindow().activeView().runCommand('findInFiles', args)

    def finish_up(self, results):
        finds, errors = results

        if not finds:
            return sublime.setTimeout (
                functools.partial(sublime.statusMessage, 'Found no files'), 100
            )
        
        results = pprint.pformat({'finds':finds, 'errors':errors})
        
        if errors:
            sublime.messageBox( 'Files couldn\'t be searched: \n\n%s' %
                                     '\n'.join(errors) )

        sublime.setClipboard(results)
        @do_in(50)
        def notify():
            'Else msgs from thread will drown it out'
            sublime.statusMessage("%s finds) %s errors) on clipboard" %
                                    (len(finds), len(errors)) )
        
################################################################################

    @threaded(finish=finish_up, msg='search already running')
    def search(self, files, pattern, is_regex, window):
        findings = []
        errors = []

        if not is_regex: pattern = re.escape(pattern)
        matcher = re.compile(pattern, re_compile_flags)
        num_files = len(files)
        self.stop_search = 0

        panel_key = `hash(datetime.datetime.now())`

        def search(search_in, f):
            if matcher.search(search_in):
                findings.append(f)

        def show_panel():
            window.showQuickPanel (
                panel_key, 'findInFiles', findings, findings,
                sublime.QUICK_PANEL_FILES | sublime.QUICK_PANEL_MULTI_SELECT
            )

        for i, f in enumerate(files):
            if self.stop_search:
                break

            @do_in(5)
            def status():
                sublime.statusMessage(" (%s of %s) ctrl+shift+z to halt %s"
                                        % (i+1, num_files, f) )

                if not self.close_panel:
                    show_panel()

            try:
                with open(f, 'r+') as fh:
                    search(mmap.mmap(fh.fileno(), 0), f)

            except Exception, e:
                try:
                    with open(f) as fh:
                        search(fh.read(), f)

                except Exception, e:
                    errors.append((f, `e`))

        @do_in(5)
        def status():
            if self.close_panel:
                show_panel()
 
        self.searching = False
        return findings, errors

class EscapeRegex(sublimeplugin.TextCommand):
    def run(self, view, args):
        for sel in view.sel():
            view.replace(sel, re.escape(view.substr(sel)))

################################################################################