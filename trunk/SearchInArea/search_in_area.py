#################################### IMPORTS ###################################

# Std Libs
import re
from functools import partial

# Sublime Modules
import sublime
import sublimeplugin

############################### HELPER FUNCTIONS ###############################

def region_range(region):
    return xrange(region.begin(), region.end())

def pts_match_selector(view, region, selector=None, match=True, cond=all):
    return  cond (
        view.matchSelector(pt, selector) is match for pt in region_range(region)
    )

def regions_equal(r1, r2):
    """ Region.__eq__ seems to compare by r.a and r.b """
    return r1.begin() == r2.begin() and r1.end() == r2.end()

def find_all(view, search, region, flags=0, P=None):
    view.sel().clear()

    pos = region.begin() #start position
    while True:
        r = view.find(search, pos, flags) #find next string
        if r is None or not region.contains(r) or pos >= region.end():
            break #string not found or past end of search area

        pos = r.end() #update current position

        if P is None or P(view, r):
            view.sel().add(r) #add to selection

################################### COMMANDS ###################################

class BookmarkArea(sublimeplugin.TextCommand):
    def run(self, view, args):
        sels = view.sel()

        # Set bookmarks
        if view.hasNonEmptySelectionRegion() or len(sels) > 1:
            region = sels[0].cover(sels[-1])

            for pos in (region.end(), region.begin()):
                sels.clear()
                sels.add(sublime.Region(pos, pos))
                view.runCommand('toggleBookmark')

        # Clear bookmarks
        else:
            sel = sels[0]

            for cmd in ('prev', 'toggle', 'next', 'toggle'):
                view.runCommand('%sBookmark' % cmd)

            sels.clear()
            sels.add(sel)

class SearchInArea(sublimeplugin.TextCommand):
    def isEnabled(self, view, args):
        return not (
         len(view.sel()) != 3 and view.word(view.sel()[0]).empty() )

    def run(self, view, args):
        sels = view.sel()
        
        if len(sels) == 3:
            start, search_sel, end = sels
        else:
            search_sel = sels[0]

            view.runCommand('prevBookmark')
            start = sels[0]

            view.runCommand('nextBookmark')
            end = sels[-1]

        ###############################################################

        full_word = view.word(search_sel)
        search_sel = search_sel or full_word
        search = re.escape(view.substr(search_sel))

        search_region = start.cover(end)
        if not search_region or regions_equal(search_sel, search_region):
            search_region = sublime.Region(0, view.size())

        ############################ OPTIONS ##########################

        flags = sublime.IGNORECASE if 'ignore_case' in args else 0

        if 'detect_whole_word' in args:
            if regions_equal(search_sel, full_word):
                search = r'\b%s\b' % search

        P = None

        if 'in_scope' in args:
            for selector in ('string', 'comment'):
                matcher = partial(pts_match_selector, selector=selector)
                if matcher(view, search_sel):
                    P = matcher
                    break

            if P is None:
                P = partial (
                    pts_match_selector,
                    selector = 'string|comment',
                    match = False,
                    cond = any )

        find_all(view, search, search_region, flags=flags, P=P)

################################################################################