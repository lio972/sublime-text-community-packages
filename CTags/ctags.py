###############################################################################

# Std Libs
import os
import re
import functools
import string

from os.path import join, normpath, dirname

# Sublime Libs
import sublime
import sublimeplugin

# User Libs
import parse_ctags

###############################################################################

def monkeypatch_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator

@monkeypatch_method(sublime.View)
def word(self, pt):
    # Takes a pt or a Region as argument
    if isinstance(pt, sublime.Region):
        pt = pt.begin()

    # Word boundary characters
    wordSeparators = self.options().get('wordSeparators') + string.whitespace

    # Backtrack looking for word boundary
    for start in range(pt, -1, -1):
        if self.substr(start) in wordSeparators:
            break 

    # Go forward looking for word boundary 
    for end in range(pt, self.size() + 1):
        if self.substr(end) in wordSeparators:
            break 

    return sublime.Region(start + 1, end)

@monkeypatch_method(sublime.View)
def fullBuffer(self):
    return self.substr(sublime.Region(0, self.size()))

@monkeypatch_method(sublime.View)
def regexRegions(self, regex):
    return [
        sublime.Region(m.start(), m.end()) for m in 
        regex.finditer(self.fullBuffer())
    ]

@monkeypatch_method(sublime.View)
def selectRegex(self, regex):
    sel_set = self.sel()

    search = self.regexRegions(regex)
    
    if search:
        sel_set.clear()
        for selection in search:
            sel_set.add(selection)


@monkeypatch_method(sublime.Window)
def isOpen(self, check):
    for v in self.views():
        fn = v.fileName()
        if fn and normpath(fn) == normpath(check):
            return True

###############################################################################
    
class NavigateToDefinitionCommand(sublimeplugin.TextCommand):
    onLoadEvents           = {}
    onActivatedEvents      = {}
    tags                   = {}
    
    def handleEvents(self, view, events):
        fn = view.fileName()
        if fn: fn = os.path.normpath(fn)
        if fn not in events: return

        search_string = events.pop(fn)

        view.selectRegex(re.compile(re.escape(search_string)))
        for t in range(5): view.runCommand('scroll 1')

    def onActivated(self, view):
        self.handleEvents(view, self.onActivatedEvents)

    def onLoad(self, view):
        self.handleEvents(view, self.onLoadEvents)

    def jump(self, view, tag_file):
        ex_command = self.tags[tag_file]
        tag_file = normpath(join(self.tag_dir, tag_file))

        window = view.window()

        if ex_command.isdigit():
            window.openFile(tag_file, int(ex_command), 1)
        else:
            if window.isOpen(tag_file):
                self.onActivatedEvents[tag_file] = ex_command
            else:
                self.onLoadEvents[tag_file] = ex_command

            window.openFile(tag_file)

    def quickOpen(self, view, files):
        window = view.window()
        window.showQuickPanel("", "navigateToDefinition", files)

    def run(self, view, args):
        if args:
            # Handle QuickOpen
            return self.jump(view, args[0])

        current_symbol = view.substr(view.word(view.sel()[0]))

        # need to memoize/cache these somehow and load in another thread
        self.tag_dir = dirname(view.fileName())
        tags = parse_ctags.parse_tag_file(join(self.tag_dir, 'tags'))

        self.tags = dict (
            (t['filename'], t['ex_command']) for t
                                             in tags.get(current_symbol, [])
        )

        if len(self.tags) > 1:     self.quickOpen(view, self.tags.keys())
        elif self.tags:            self.jump(view, self.tags.keys()[0])
        
################################################################################