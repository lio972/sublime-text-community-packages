"""
Sublime Text - PowerUser Package
By: EJ12N
Plugin Code By: Sublimator
"""
import pprint, functools, re
import sublime
import sublimeplugin

################################### SETTINGS ###################################

SLOW_MOTION = 0

################################ STOP CONDITIONS ###############################

QUOTES = '["\']'

def direction_extent_index(d):
    return (d -1) / 2

character_is_quote = ( lambda v, c:
                            re.match (
                                c.looking_for,
                                v.substr (
                                    v.sel()[0].begin()  +
                                    direction_extent_index(c.direction) )
                        ))

def update_context(v, c):
    sel_set = v.sel()

    cursor = sel_set[0].begin()

    behind1 = v.substr(cursor + direction_extent_index(c.direction) -1)
    behind2 = v.substr(cursor + direction_extent_index(c.direction) -2)

    if  behind1 == '\\' and behind2 != '\\':
        return c,   False

    c.setdefault('stop_regions', []).append(sel_set[0])

    # re_instate starting point
    if c.direction == -1:
        c['looking_for'] = v.substr(cursor -1)
        sel_set.clear()
        sel_set.add(c.start_sel)

    return c, True

start_context = dict (
    looking_for  =  QUOTES,
)

actions = (
    # key   # stop_condition   # contexter
    (  "Character behind cursor is a quote",
       character_is_quote,
       update_context ),
)

#################################### HELPERS ###################################

class Context(dict):
    "Sugar"
    __setattr__ = dict.__setitem__
    __getattr__ = lambda s, a: s[a]

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

############################# SELECT STRING COMMAND ############################

class SelectString(sublimeplugin.TextCommand):
    def run(self, view, args):
        if SLOW_MOTION:
            return staggered(SLOW_MOTION)(self.select)(view, args)
        else:
            for yield_pt in self.select(view, args): pass

    def select(self, view, args):
        sel_set = view.sel()
        start_points = list(sel_set)
        finds = []

        while start_points:
            sel_set.clear()
            sel_set.add(start_points.pop())

            c = Context(start_context.copy())
            c.start_sel = sel_set[0]

            for direction in (-1, 1):
                c.direction = direction

                while True:
                    fails = {}

                    for key, expr, context_check  in actions:
                        stop_cond = expr(view, c)

                        if stop_cond:
                            c, met_condition = context_check(view, c)

                            if met_condition:
                                fails[key] = stop_cond

                    if fails:
                        break
                    else:
                        yield view.runCommand('move characters %s' % direction)
                        pos = sel_set[0].begin()

                        if pos == 0 or pos == view.size():
                            break

            region = c.stop_regions[0]
            for reg in c.stop_regions[1:]:
                region = region.cover(reg)

            finds.append(region)

        map(sel_set.add, finds)

################################################################################