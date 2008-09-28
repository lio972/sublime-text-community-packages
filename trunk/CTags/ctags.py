###############################################################################

# Std Libs
import os
import time
import re
import functools

from os.path import join, normpath

# Sublime Libs
import sublime
import sublimeplugin

# User Libs
import parse_ctags

###############################################################################

def replace_selections(view, sel):
    view.sel().clear()
    view.sel().add(sel)

###############################################################################
    
class NavigateToDefinitionCommand(sublimeplugin.TextCommand):
    callbacks = {}
    
    def onLoad(self, view):
        fn = view.fileName()
        if fn: fn = os.path.normpath(fn) 
        if fn not in self.callbacks: return

        search_string = self.callbacks.pop(fn)    
        v_str = view.substr(sublime.Region(0, view.size()))

        if search_string in v_str:
            pt = v_str.index(search_string)
            sel = sublime.Region(pt, pt)
            replace_selections(view, sel)

            # This scrolls the view to the selection as well as to the
            # beginning of the line
            view.runCommand('moveTo bol')
            for t in range(5): view.runCommand('scroll -1')

    onActivated = onLoad

    def run(self, view, args):
        # Get a reference to the active window
        window = view.window()
        
        # Store current selection for later
        first_sel = view.sel()[0]

        # Expand selection to word to get "symbol under cursor"
        view.runCommand('expandSelectionTo word')
        current_symbol = view.substr(view.sel()[0])

        # Get the dir of the current file
        tag_dir = os.path.dirname(view.fileName())

        # Clear the selection and replace with original un-word-expanded sel
        replace_selections(view, first_sel)

        # need to memoize/cache these somehow and load in another thread
        tags = parse_ctags.parse_tag_file(os.path.join(tag_dir, 'tags'))

        for tag in (parse_ctags.Tag(t) for t in tags.get(current_symbol, [])):
            if tag.ex_command.isdigit():
                window.openFile(tag.filename, int(tag.ex_command), 1)
            else:
                tag_file = normpath(join(tag_dir, tag.filename))
                self.callbacks[tag_file] = tag.ex_command
                window.openFile(tag_file)

################################################################################