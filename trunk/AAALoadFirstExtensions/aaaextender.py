#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

import os
import sublime
import sublimeplugin

from pluginhelpers import ( SublimeOptions, SublimeMacro, patches,
                            addSublimePackage2SysPath, onIdle, threaded,
                            FocusRestorer )

################################################################################

addSublimePackage2SysPath('AAALoadFirstExtensions')
addSublimePackage2SysPath('AAALoadFirstExtensions', 'site-packages')

################################################################################

sublimeplugin.onIdle = onIdle
sublimeplugin.threaded = threaded
sublime.FocusRestorer = FocusRestorer

################################ MONKEY PATCHES ################################
# Do not rely on any of these, they are just there for messing around with own
# plugins. They may be shipped off.
################################################################################

# Nicer repr
@patches(sublime.View)
def __repr__(s):
    return "<View (id=%r bufferId=%r, fileName=%r)>" % (
        s.id(), s.bufferId(), os.path.basename( s.fileName() or '') )

# Iterate over the points in a region
@patches(sublime.Region)
def __iter__(self):
    for pt in xrange(self.begin(), self.end()):
        yield pt

@patches(sublime.View, property)
def buffer(v):
    return v.substr(sublime.Region(0, v.size()))

@patches(sublime.View, property)
def option(s): return SublimeOptions(s)

@patches(sublime.View, property)
def cmd(s): return SublimeMacro(s)

@patches(sublime.View, property)
def cursor(s):
    sels = s.sel()
    if len(sels) > 0:
        return sels[0].begin()

@patches(sublime.View)
def cursor_matches(s, selector):
    return s.matchSelector(s.sel()[0].begin(), selector)

@patches(sublime.View, property)
def scope(s):
    pt = s.sel()[0].begin()
    return " ".join (
         t.strip() for t in reversed(s.syntaxName(pt).split())
    )

@patches(sublime.Window, property)
def cmd(s): return SublimeMacro(s)

sublime.View.cb = property( lambda s: sublime.getClipboard(),
                            lambda s, o: sublime.setClipboard(o))

################################################################################