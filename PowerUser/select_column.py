"""
Sublime Text - PowerUser Package
By: EJ12N
Plugin Code By: Nicholas (Sublimator)
!Experimental!
"""
#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

import pprint
import functools

# Sublime Libs
import sublime
import sublimeplugin

# from geniusql.logic import Expression as E  # Overkill, trying it out

E = lambda e: e

################################### CONSTANTS ##################################

index_selection_by_direction = {-1:    0,     1:     -1}
direction_by_name            = {-1: 'up',     1: 'down'}

STARS = '*' * 30

################################### SETTINGS ###################################

SLOW_MOTION = 0 # ms delay per `yield` to Sublime
                # Set at high values to see rendering of command in slow mo,
                # or to any value with boolean evaluation of False
                # to run normally. Handy for debugging customisations and to
                # `see` what is going on.

DEBUG = SLOW_MOTION or 0

################################ STOP CONDITIONS ###############################

# Stop conditions are those that stop the cursor moving up / down

# When in slow motion motion mode, will log all failing stop conditions
# as well as pretty print the locals().

# Uses geniusql ast Expressions; which can be strung together if needed
# eg:       (e1 | e2) & e3.

# Will print a nice __repr__ of Expressions too (locals pprint)

stop_conds = {
    "New area doesnt match start scope": E (
        lambda v, sel, new_sel, c:
            not v.matchSelector(new_sel.begin(), c.start_scope)),

    "Behind cursor is not space but is on new cursor": E (
        lambda v, sel, new_sel, c:
            not v.substr(sel.begin()-1).isspace()
            and v.substr(new_sel.begin()-1).isspace() ),

    "Behind cursor is space but behind new cursor isn't": E (
        lambda v, sel, new_sel, c:
            v.substr(sel.begin()-1).isspace()
            and not v.substr(new_sel.begin()-1).isspace() ),

    "Cursor is space but new cursor isn't": E (
        lambda v, sel, new_sel, c:
            v.substr(sel.begin()).isspace()
            and not v.substr(new_sel.begin()).isspace() ),

    "Cursor isn't space but new cursor is": E (
        lambda v, sel, new_sel, c:
            not v.substr(sel.begin()).isspace()
            and v.substr(new_sel.begin()).isspace() ),

    # Usually only hit on rare cases
    "Different Start Point" :  E (
        lambda v, sel, new_sel, c: c.new_start_pt  != c.start_pt ),

    'selectLines was noop'  : E (lambda v, sel, new_sel, c: c.going_nowhere),

    # Unlikely to need this due to `cursor is space but ... ` type conditions
    # "Hit a blank Blank line" : E (
    #     lambda v, sel, new_sel, c:
    #       view.substr(view.line(new_sel)).isspace() ),
}

#################################### HELPERS ###################################

class Context(dict):
    "Sugar"
    __setattr__ = dict.__setitem__
    __getattr__ = lambda s, a: s[a]

def expanded_tabs_region_length(view, start, end):
    tab_size = int(view.options().get('tabSize', 8))
    region = sublime.Region(start, end)
    return len(view.substr(region).expandtabs(tab_size))

def get_sel_pts(view, sel):
    "Tab normalized character point"
    start   =  expanded_tabs_region_length(view, view.line(sel).begin(), sel.begin())
    length  =  expanded_tabs_region_length(view, sel.begin(), sel.end())
    return start, length

def staggered(every=1):
    "Slow mowifier"
    def coRoutine(f):
        @functools.wraps(f)
        def run(*args):
            routine = f(*args)

            def next():
                try:                   routine.next()
                except StopIteration:  return
                sublime.setTimeout(next, every)

            next()
        return run
    return coRoutine

normed_scope = lambda v, pt: " ".join (
     t.strip() for t in reversed(v.syntaxName(pt).split()) )

################################################################################

class SelectColumn(sublimeplugin.TextCommand):
    isEnabled = lambda s,v,a: len(v.sel())

    def run(self, view, args):
        if SLOW_MOTION:
            return staggered(SLOW_MOTION)(self.select)(view, args)
        else:
            for yield_pt in self.select(view, args): pass

    def select(self, view, args):
        if DEBUG: print STARS, "COLUMN SELECT COMMAND", STARS

        # All selections from all potential columns ( col per starting_pt )
        all_selections = []

        # Save all the starting collections:
        start_selections = []
        starting_points = set()

        for sel in view.sel():
            start_pt, length = get_sel_pts(view, sel)
            if start_pt not in starting_points:
                starting_points.add(start_pt)
                start_selections.append((sel, start_pt, length))

        yield view.sel().clear()

        for sel, start_pt, length in start_selections:
            c = Context(start_pt=start_pt)

            view.sel().add(sel)
            c.start_scope = normed_scope(view, sel.begin())

            # If there is a non empty selection make it empty first for purposes
            # of expansion. Move to begin(), command will reinstate length
            # later. Works around selection direction LtR, RtL complications

            if length:
                view.runCommand('move', ['characters', '-1'])


            # Foreach direction move cursor that way until hit stop condition
            for direction in (1, -1):
                sel_index = index_selection_by_direction.get(direction)
                rollback_selectLines = False

                while True:
                    # Keep track of number of selections
                    sels = list(view.sel())
                    num_sels_b4 = len(view.sel())

                    # selectLines
                    yield view.runCommand('selectLines', [`direction`])

                    # see if selectLines was a noop
                    c.going_nowhere = num_sels_b4 == len(view.sel())
                    if c.going_nowhere:
                        assert sels == list(view.sel())

                    if not c.going_nowhere:
                        # If extra cursor was added make sure it doesn't
                        # hit a stop condition
                        new_sel = view.sel()[sel_index]
                        c.new_start_pt, new_end_pt = get_sel_pts(view, new_sel)

                        fails,  fail_expr = {}, []
                        for key,  expr  in sorted(stop_conds.items()):
                            stop_cond = expr(view, sel, new_sel, c)
                            if stop_cond:
                                fails[key] = stop_cond
                                fail_expr.append(expr)
                                if not SLOW_MOTION:
                                    break

                        if fails:
                            rollback_selectLines = True

                            if DEBUG:
                                direction = direction_by_name[direction]

                                print '\nSTOP COND: %s' % direction
                                print '\n\n%s' % pprint.pformat(fails)
                                print '\n\n%s' % pprint.pformat(locals())

                    if c.going_nowhere or rollback_selectLines:
                        break

                # Delete cursor that hit stop condition
                if rollback_selectLines:
                    yield view.sel().subtract(new_sel)

            for sel in view.sel():
                yield all_selections.append (
                    sublime.Region(sel.begin(), sel.begin()+length ))

            view.sel().clear()

        for sel in all_selections:
            view.sel().add(sel)

################################################################################