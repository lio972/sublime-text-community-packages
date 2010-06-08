import copy
import sublime
import sublimeplugin

class DuplicateLine(sublimeplugin.TextCommand):
    def run(self, view, args):
        clipboard = sublime.getClipboard()
        sel = view.sel()
        initial_selection = [s for s in sel]
        sel.clear()

        adjusted_selection = []
        accumulated_selection_size = 0

        for s in initial_selection:
            s = self.adjustPosition(s, accumulated_selection_size)
            adjusted_selection.append(s)
            sel.add(s)
            view.runCommand("expandSelectionTo line")
            accumulated_selection_size += self.selectionSize(sel[0])
            view.runCommand("copy")
            view.runCommand("move characters 1")
            view.runCommand("paste")
            sel.clear()

        [sel.add(s) for s in adjusted_selection]

        sublime.setClipboard(clipboard)

    def selectionSize(self, region):
        return region.end() - region.begin()

    def adjustPosition(self, region, increment):
        if increment > 0:
            region = sublime.Region(region.begin() + increment, region.end() + increment)

        return region
