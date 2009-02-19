################################################################################
# Std Libs

from __future__ import with_statement

import re
import os
import functools

from os.path import dirname, split, join, splitext, normpath

# Sublime Modules

import sublime
import sublimeplugin
import os
import time
import glob
import mmap
import threading
import pprint

# User Libs

from plugin_helpers import wait_until_loaded, view_fn, threaded
from walk_files import find_files

################################################################################

PANEL_SYNTAXES = [
    "Packages/Text/Plain text.tmLanguage",
    "Packages/Regular Expressions/RegExp.tmLanguage",
]

def is_regex_search(view):
    return PANEL_SYNTAXES.index(view.options().get('syntax'))

################################################################################

def timeout(f):
    return sublime.setTimeout(f, 10)

def show_find_panel(window):
    window.runCommand('hidePanel')
    window.runCommand('showPanel find')

def full_buffer(view):
    return view.substr(sublime.Region(0, view.size()))

def replace_full_buffer(view, replacement):
    view.replace(sublime.Region(0, view.size()), replacement)

################################################################################

class FindInFiles(sublimeplugin.TextCommand):
    def __init__(self):
        self.reset()
    
    def isEnabled(self, view, args):
        return self.state != 3
    
    def reset(self):
        self.pattern    = None
        self.file_mask  = None
        self.wd         = None
        self.is_regex   = None
        self.state      = 1

    def run(self, view, args):
        if args:
            if 'reset' in args:
                return self.reset()
        
        window = view.window()
        self.window = window        
        
        # This will always return the currently active file
        activeView = window.activeView()
        
        # Is the `view` a reference to the find panel?
        syntax = view.options().get('syntax')
        view_is_find_panel= (
            syntax in PANEL_SYNTAXES and 
            view.fileName() != activeView.fileName() ) 
            
        if view_is_find_panel:
            getattr(self, 'command%s' % self.state)(view, activeView)
            self.state += 1
        else:
            sublime.statusMessage('FindInFiles Reset')
            self.reset()
    
    def command1(self, panel, activeView):
        self.pattern = full_buffer(panel)
        # print self.state, `self.pattern`
                
        fn = activeView.fileName()
        
        self.is_regex = is_regex_search(panel)
        self.wd = normpath(dirname(fn))
        
        ext = splitext(fn)[1]
        
        if self.is_regex:
            mask = '.\\;%s$' % ('.*' + re.escape(ext))
            msg = 'Enter file mask $PATH(recursive);$REGEX'
        else:
            mask = '.\\*' + ext
            msg = 'Enter file mask $PATH/$GLOB'

        replace_full_buffer(panel, mask)
        panel.sel().clear()
        panel.sel().add(sublime.Region(1, 1))

        sublime.statusMessage(msg)

    def command2(self, panel, activeView):
        self.mask = full_buffer(panel)
        replace_full_buffer(panel, self.pattern)
        
        if not self.is_regex:
            self.pattern = re.escape(self.pattern)
        
        self.search(self.pattern, self.mask, self.wd, is_regex_search(panel))

    def finish(self, results):
        finds, errors = results
        
        if not finds: sublime.statusMessage('Found no files')
        else:
            results = 'Finds:\n%s\nErrors:\n%s' % \
                       tuple(map(pprint.pformat, [finds, errors]))

            sublime.setClipboard(results)

            @timeout
            def notify():
                'Else msgs from thread will drown it out'
                sublime.statusMessage('Results are on clipboard as python list')

        if len(finds) > 1000:
            self.window.showQuickPanel ( "",
                'open', finds
            )
        else:
            for f in finds:
                @wait_until_loaded(f)
                def and_then(view):
                    self.window.focusView(view)
                    self.window.runCommand('findAll')

        self.reset()

################################################################################

    @threaded(finish=finish, msg='search already running')
    def search(self, search, mask, wd, mask_is_regex):
        findings = []
        errors   = []
        
        matcher = re.compile(search, re.M)
        
        if mask_is_regex:        files = find_files(wd, mask)
        else:                    files = glob.glob(normpath(join(wd, mask)))

        MB_10 = 10 * (2 ** 20) 

        for f in files:
            print f
            
            @timeout
            def status():
                sublime.statusMessage(f)
            
            try:
                with open(f, 'r+') as fh:
                    try:
                        mapping = mmap.mmap(fh.fileno(), 0)
                        if matcher.search(mapping): findings.append(f)

                    except Exception, e:
                        errors.append((f, `e`))
            
                    finally:
                        try: mapping.close()
                        except UnboundLocalError, e:
                            pass

            except IOError, e:
                errors.append((f, `e`))
                
        return findings, errors

################################################################################

class EscapeRegex(sublimeplugin.TextCommand):
    def run(self, view, args):
        for sel in view.sel():
            view.replace(sel, re.escape(view.substr(sel)))