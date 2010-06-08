import copy
import sublime
import sublimeplugin

class DuplicateLineAndToggleComment(sublimeplugin.TextCommand):
    def run(self, view, args):

        clipboard = sublime.getClipboard()

        sel = view.sel()
        initial_selection = [s for s in sel]
        sel.clear()

        adjusted_selection = []
        accumulated_shift = 0

        for s in initial_selection:
            s = self.adjustPosition(s, accumulated_shift)
            adjusted_selection.append(s)
            sel.add(s)
            view.runCommand("expandSelectionTo line")
            accumulated_shift += sel[0].end() - sel[0].begin()
            view.runCommand("copy")
            begin = sel[0].begin()
            end = sel[0].end()
            view.runCommand("toggleComment")
            accumulated_shift += sel[0].end() - end
            self.gotoPosition(sel, begin)
            view.runCommand("paste")
            sel.clear()

        [sel.add(s) for s in adjusted_selection]

        sublime.setClipboard(clipboard)

    def adjustPosition(self, region, increment):
        if increment > 0:
            region = sublime.Region(region.begin() + increment, region.end() + increment)
        return region

    def gotoPosition(self, sel, pos):
        sel.clear()
        sel.add(sublime.Region(pos, pos))
