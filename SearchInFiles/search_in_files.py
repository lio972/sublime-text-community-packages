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

from itertools import chain
from os.path import dirname, split, join, splitext, normpath

# Sublime Modules

import sublime
import sublimeplugin

# User Libs
from plugin_helpers import wait_until_loaded, view_fn, threaded

################################################################################

PANEL_SYNTAXES = [
    "Packages/Text/Plain text.tmLanguage",
    "Packages/Regular Expressions/RegExp.tmLanguage",
]

def is_regex_search(view):
    return PANEL_SYNTAXES.index(view.options().get('syntax'))

################################################################################

STOP, NEXT = object(), object()

def timeout(f):
    return sublime.setTimeout(f, 10)

def show_find_panel():
    window = sublime.activeWindow()
    window.runCommand('hidePanel')
    window.runCommand('showPanel find')

def view_is_find_panel(view):
    # Is the `view` a reference to the find panel?
    syntax = view.options().get('syntax')
    return (
        # in case of untitled view, `None != None`
        syntax in PANEL_SYNTAXES and 
        view.fileName() != sublime.activeWindow().activeView().fileName() ) 

def full_buffer(view):
    return view.substr(sublime.Region(0, view.size()))

################################################################################

class FindInFiles(sublimeplugin.TextCommand):
    routine = None
    
    def isEnabled(self, view, args):
        enabled = args or view_is_find_panel(view)
        if not enabled:
            show_find_panel()
            self.routine = None
        else:
            return 1

    def run(self, view, args):
        if self.routine is None:
            self.routine = self.co_routine(view, args)
            self.routine.next() # Initiate

        ret  = self.routine.send(args)
        if ret is STOP: 
            self.routine = None

    def co_routine(self, view, args):
        yield # Initiate

        window = sublime.activeWindow()

        try:
            sublimeplugin.allCommands[1]['jumpBack'].append(window.activeView())
        except Exception, e:
            pass

        is_regex = is_regex_search(view)
        
        mount_points = window.project().mountPoints()
        mount_paths = [d['path'] for d in mount_points]
        
        if len(mount_paths) > 1:
            sublime.activeWindow().showQuickPanel ( "",'findInFiles', 
                    mount_paths,
                    mount_paths,
                    sublime.QUICK_PANEL_MULTI_SELECT )

            mount_paths = (yield)
            mount_points = [d for d in mount_points if d['path'] in mount_paths]

        files = list (
            chain(*(d['files'] for d in mount_points)) )

        self.search(files, full_buffer(view), is_regex)

        for f in (yield):
            @wait_until_loaded(f)
            def and_then(view):
                w = sublime.activeWindow()
                w.focusView(view)
                w.runCommand('findAll')
 
        yield STOP
        
    def finish(self, results):
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

        sublime.activeWindow().showQuickPanel (
             "",'findInFiles', 
            [f[1] for f in finds],
            ['(%3s) %s' % f for f in finds],
            sublime.QUICK_PANEL_FILES | sublime.QUICK_PANEL_MULTI_SELECT
         )

################################################################################

    @threaded(finish=finish, msg='search already running')
    def search(self, files, pattern, is_regex):
        findings = []
        errors = []

        if not is_regex: pattern = re.escape(pattern)
        matcher = re.compile(pattern, re.M)

        for f in files:
            @timeout
            def status():
                sublime.statusMessage(f)

            with open(f, 'r+') as fh:
                def search(search_in):
                    matches = matcher.findall(search_in)
                    if matches:
                        findings.append((len(matches), f))
                try:
                    search(mmap.mmap(fh.fileno(), 0))

                except Exception, e:
                    try:
                        fh.seek(0)
                        search(fh.read())

                    except Exception, e:
                        errors.append((f, `e`))

        return sorted(findings, reverse=True), errors

class EscapeRegex(sublimeplugin.TextCommand):
    def run(self, view, args):
        for sel in view.sel():
            view.replace(sel, re.escape(view.substr(sel)))

################################################################################