#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs

import re
import os
import textwrap

# Sublime Libs
import sublime
import sublimeplugin

############################### COMMON FUNCTIONS ###############################

def strip_preceding(selection, padding="", rstrip=True):
    "Strips preceding common space so only relative indentation remains"

    preceding_whitespace = re.compile("^(?:(\s*?)\S)?")
    common_start = len(selection)

    split = selection.split("\n")
    for line in (l for l in split if l.strip()):
        for match in preceding_whitespace.finditer(line):
            common_start = min(match.span(1)[1], common_start)
            if common_start == 0: break

    stripped = "\n".join( [split[0][common_start:]]  +
                       [padding + l[common_start:] for l in split[1:]] )

    return  stripped.rstrip("\n") if rstrip else stripped

def lines_get_firsts_displacement(view, region):
    """

    Expands a selection to encompass the lines it is situated in.
    It then contracts the start point to where the first non space
    character is found. Returns the start pt of the expanded
    selection, displacement( characters to contracted selection),
    and then the end pt.

    """

    region = view.line(region)
    start, end = region.begin(), region.end()
    displace = 0
    for x in xrange(start, end):
        if view.substr(x).isspace():
            displace += 1
        else: break
    return start, end, displace

def line_regions_first_no_preceding(view, region):
    """

    Expands a selection to encompass the lines it is situated in.
    It then contracts the start point to where the first non space
    character is found. Returns a region

    """

    start, end, displace = lines_get_firsts_displacement(view, region)
    return sublime.Region(start+displace, end)

def get_tab(view):
    """

    Gets a series of empty space characters of size 'tabSize', the
    current views setting for size of tab

    """

    return view.options().get('tabSize') * " "

def substr_strip_common_preceding(view, region, pad_secondary=""):
    """

    Takes a view, and a Region of it, strips preceding common space
    so only relative indentation remains

    """

    region = view.line(region)
    tab = get_tab(view)
    sel = view.substr(region).expandtabs(int(view.options().get('tabSize', 8)))
    return strip_preceding(sel, padding = pad_secondary or tab)

################################# PASTE HELPERS ################################

def insert_or_replace(view, region, string):
    if region:
        return view.replace(region, string)
    else:
        return view.insert(region.begin(), string)

########################### TAB NORMALIZATION HELPERS ##########################

def handle_tabs(view, string, offset=0):
    if not view.options().get('translateTabsToSpaces'):
        tab_size = view.options().get('tabSize', 8)

        string = unexpand(string, tab_size, offset)

    return string

def get_tab_size(view):
    return int(view.options().get('tabSize', 8))

def normed_indentation_pt(view, sel):
    """  Calculates tab normed `visual` position of sel.begin() relative "
        to start of line 

        \n\t\t\t    => normed_indentation_pt => 12
        \n  \t\t\t  => normed_indentation_pt => 12

        Different amount of characters, same visual indentation.
    """

    tab_size = get_tab_size(view)
    pos = 0

    for pt in xrange(view.line(sel).begin(), sel.begin()):
        if view.substr(pt) == '\t':
            pos += tab_size - (pos % tab_size)
        else:
            pos += 1

    return pos

def compress_column(column, tab_size):
    if all(c.isspace() for c in column):
        column = '\t'

    elif column[-1] == ' ':
        while column and column[-1] == ' ':
            column.pop()
        column.append('\t')

    return column

def unexpand(the_string, tab_size, first_line_offset = 0):
    lines = the_string.split('\n')
    compressed = []

    for li, line in enumerate(lines):
        pos                =      0

        if not li: pos += first_line_offset

        rebuilt_line       =     []
        column             =     []

        for char in line:
            column.append(char)
            pos += 1

            if char == '\t':
                pos += tab_size - (pos % tab_size)

            if pos % tab_size == 0:
                rebuilt_line.extend(compress_column(column, tab_size))
                column = []

        rebuilt_line.extend(column)
        compressed.append(''.join(rebuilt_line))

    return '\n'.join(compressed)

################################ UN/EXPAND TABS ################################

class TabCommand(sublimeplugin.TextCommand):
    def isEnabled(self, view, args):
        if 'set' in args or not self.translate:
            view.options().set('translateTabsToSpaces', self.translate)

        if not view.hasNonEmptySelectionRegion():
            view.runCommand('selectAll')

        return True

class ExpandTabs(TabCommand):
    translate = True

    def run(self, view, args):
        tab_size = int(view.options().get('tabSize', 8))

        for sel in view.sel():
            view.replace(sel, view.substr(sel).expandtabs(tab_size))

class UnexpandTabs(TabCommand):
    translate = False

    def run(self, view, args):
        tab_size = get_tab_size(view)

        for sel in view.sel():
            the_string = view.substr(sel)
            first_line_off_set = normed_indentation_pt( view, sel ) % tab_size

            compressed = unexpand(the_string, tab_size, first_line_off_set)
            view.replace(sel, compressed)

################################################################################

class RelativeIndent(sublimeplugin.TextCommand):
    def run(self, view, args):
        sels = view.sel()

        if args[0] == 'paste':
            clip = sublime.getClipboard().expandtabs(get_tab_size(view))

            clip = textwrap.dedent(clip).rstrip().split(u'\n')
            n = len(clip)

            if len(sels) > 1: # Columnar Paste
                for region in view.sel():
                    insert_or_replace(view, region, clip.pop(0))
            else:
                cursor_at = normed_indentation_pt(view, view.sel()[0])

                for i, l in enumerate(clip):

                    padding = (cursor_at * ' ') if i else ''

                    line = handle_tabs(view,  padding + l)
                    insert_or_replace(view, view.sel()[0], line)

                    if not i+1 == n:
                        view.runCommand('moveTo eol')
                        view.runCommand('insertAndDecodeCharacters', ['\n'])
                        view.erase(view.line(view.sel()[0]))

        else:
            for sel in view.sel(): view.sel().add(view.line(sel))
            view.runCommand(args[0])

class RelativeIndentSnippet(sublimeplugin.TextCommand):
    def run(self, view, args):
        sel_set = view.sel()

        for sel in sel_set:
            if sel.empty(): continue

            selection_stripped = handle_tabs ( view,
                substr_strip_common_preceding(view, sel).rstrip() )

            modified_region = line_regions_first_no_preceding(view, sel)
            sel_set.subtract(sel)
            sel_set.add(modified_region)
            view.replace(modified_region, selection_stripped)

        view.runCommand('insertSnippet', args)

################################################################################