# coding: utf8
#################################### IMPORTS ###################################

# Future Imports 

from __future__ import with_statement

# Sublime imports 
import sublime
import sublimeplugin

# Std Lib imports
from itertools import islice, chain
from os.path import normpath
import functools
import re

################################### CONSTANTS ##################################

REGEX_SYNTAX = "Packages/Regular Expressions/RegExp.tmLanguage"
TEXT_SYNTAX  = "Packages/Text/Plain text.tmLanguage"

################################## DECORATORS ##################################

def do_in(t=0):
    def timeout(f):
        return sublime.setTimeout(f, t)
    return timeout

def onIdle(ms=50):
    def decorator(func):
        func.pending = 0
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            def idle():
                func.pending -= 1
                if func.pending is 0:
                    func(*args, **kwargs)
            func.pending +=1
            sublime.setTimeout(idle, ms)
        return wrapped
    return decorator

def co_routine(f):
    @functools.wraps(f)
    def run(*args):
        routine = f(*args)

        def next():
            try:                   routine.next()
            except StopIteration:  return
            sublime.setTimeout(next, 5)
    
        next()
    return run

def joining(sels):
    if not sels: return sels
    contigs = [sels[0]]
    
    for sel in sels:
        if abs(sel.begin() - contigs[-1].end()) <= 1:
            contigs[-1] = contigs[-1].cover(sel)
        else:
            contigs.append(sel)
    return contigs

############################### HELPER FUNCTIONS ###############################

def find_all(view, regex, flags=0):
    regions = [sublime.Region(0, 0)]

    while True:
        regions.append(view.find(regex, regions[-1].end(), flags))
        if not regions[-1] or (regions[-1] == regions[-2]):
            break

    for region in (r for r in islice(regions, 1, None) if r is not None):
        yield region

def wait_until_loaded(file):
    def wrapper(f):
        sublime.addOnLoadedCallback(file, f)
        sublime.activeWindow().openFile(file)
    return wrapper

def select_all(view, regions):
    view.sel().clear()
    for region in joining(list(regions)):
        view.sel().add(region)

def handle_caps(split):
    W = "%s[a-zA-Z0-9]+"
    A = r'(?<=[^a-zA-Z0-9])%s(?=[^\\]*$)'

    resplit= []

    for chunk in split:
        if re.match('^[A-Z ]+$', chunk):
            for c in chunk.strip():
                resplit.append(A % (W % c))
        else:
            resplit.append(chunk)

    return resplit

############################### SET REGEX COMMAND ##############################

class SetRegex(sublimeplugin.TextCommand):
    def run(self, view, args):
        print view.options().set('syntax', REGEX_SYNTAX)

################################## LIST FILTER #################################

class FilterList(sublimeplugin.TextCommand):
    last = None

    @co_routine
    def run(self, view, args):
        window = sublime.activeWindow()

        mount_points = window.project().mountPoints()
        mount_paths = [d['path'] for d in mount_points]
        files_to_search = list( chain(*(d['files'] for d in mount_points)) )

        # create the file if need be and then open it
        with open('C://listFilter.txt', 'w') as fh:
            yield window.openFile('C://listFilter.txt')
        
        av = window.activeView()
        full_buf = lambda: sublime.Region(0, av.size())

        @do_in(1)
        def l8r():
            av.replace(full_buf(), '\n'.join(files_to_search))
            av.sel().clear()
            av.show(sublime.Region(0, 0))

        def on_cancel():
            norm = lambda s: normpath(s).lower()
            if norm(window.activeView().fileName()) == norm('C://listFilter.txt'):
                window.runCommand('save')
                window.runCommand('close')

        @co_routine
        def on_done(s):
            filtered_list = av.substr(full_buf()).split('\n')

            yield on_cancel()

            if len(filtered_list) < 16:
                yield sublime.runCommand('newWindow')

                window = sublime.activeWindow()
    
                for f in filtered_list:
                    yield window.openFile(f)

        @onIdle(50)
        def on_change(s):
            chunks,  nots, highlights = [], [], []
            P = lambda o: o.strip() and not all(c == '.' for c in o.strip())

            split = filter(P, re.findall(r"(\S+(?:\s+)?)", s))

            for chunk in handle_caps(split):
                if chunk.startswith('!'):
                    chunk = chunk[1:]
                    if chunk.strip():
                        if chunk[-1] == ' ':
                            nots.append(re.compile(chunk.strip(), re.I))
                        else:
                            highlights.append(chunk.strip().rstrip('|'))
                else:
                    chunk = chunk.strip()
                    if chunk.endswith('|'):
                        highlights.append(chunk.strip('|'))
                    else:
                        chunks.append(chunk)
            
            print chunks
            
            compiled = [re.compile(c, re.I) for c in chunks]

            lines = [ l for l in files_to_search if
                      all(c.search(l) for c in compiled) and
                      all(not c.search(l) for c in nots) ]

            av.replace(full_buf(), '\n'.join(lines))
            pattern = '|'.join(('(%s)' % c) for c in chunks + highlights)
            select_all(av, find_all(av, pattern, sublime.IGNORECASE))

        sublime.activeWindow().showInputPanel (
            'Enter Search: ',  self.last or '', on_done, on_change, on_cancel )

############################## INCREMENTAL FINDALL #############################

class IncrementalFindAll(sublimeplugin.TextCommand):
    last = None
    def run(self, view, args):
        def on_done(s):
            self.last = s

        def on_cancel(): pass

        @onIdle(50)
        def on_change(s):
            self.last = s
            select_all(view, find_all(view, s))

        view.window().showInputPanel (
            'Enter Search: ',  self.last or '', on_done, on_change, on_cancel )

################################################################################