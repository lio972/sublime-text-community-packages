################################################################################

import sublime, sublimeplugin
import os

from pluginhelpers import staggered
from quickpanelcols import format_for_display

from operator import itemgetter as iget

################################################################################

class CloseAndDelete(sublimeplugin.TextCommand):
    def run(self, view, args):
        fn = view.fileName()
        view.window().runCommand('close')
        if fn: os.remove(fn)

class QuickCloseCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        views = window.views()
        active_view = window.activeView()
        if not views: return

        for v in views:
            args.append (
                (
                    v.isDirty() and '*' or ' ',
                    v.fileName() or v.name() or '<untitled>',
                    v.id(),
                )
            )

        args = sorted(args)
        files = [`f[-1]` for f in args ]
        display = format_for_display(args, cols = (0, 1))

        window.showQuickPanel("", "closeHeaps", files, display, 1 | 2 | 4 )

class CloseHeapsCommand(sublimeplugin.WindowCommand):
    @staggered(0)
    def run(self, window, args):
        active_view = window.activeView()

        args = map(eval, args)
        views = window.views()

        for v in views:
            if v.id() in args:
                yield window.focusView(v)
                yield window.runCommand('close')

        if active_view.id() in [v.id() for v in window.views()]:
            window.focusView(active_view)

################################################################################