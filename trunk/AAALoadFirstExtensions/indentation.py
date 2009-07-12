#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import re
import os
import textwrap

# Sublime Libs
import sublime

################################ STRIP PRECEDING ###############################

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

def substr_strip_common_preceding(view, region, pad_secondary=""):
    """

    Takes a view, and a Region of it, strips preceding common space
    so only relative indentation remains

    """

    region = view.line(region)
    tab = get_tab(view)
    sel = view.substr(region).expandtabs(int(view.options().get('tabSize', 8)))
    return strip_preceding(sel, padding = pad_secondary or tab)

############################### INSERT / REPLACE ###############################

def insert_or_replace(view, region, string):
    if region:
        return view.replace(region, string)
    else:
        return view.insert(region.begin(), string)

############################### TAB NORMALIZATION ##############################

def get_tab(view):
    """

    Gets a series of empty space characters of size 'tabSize', the
    current views setting for size of tab

    """

    return view.options().get('tabSize') * " "

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

################################################################################