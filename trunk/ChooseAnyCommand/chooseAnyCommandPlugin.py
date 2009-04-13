#
# Choose Any Command -- lets you choose any runnable command.
# 
import sublime, sublimeplugin, os

import inspect, sys

def cmd_runners(window):
  return  dict (
    text         = window.activeView(),
    window       = window,
    application  = sublime
  )

class ChooseAnyCommandCommand(sublimeplugin.WindowCommand):
  def run(self, window, args):
    to_sort = []

    for cmd_type, runner in cmd_runners(window).items():
      cmds_of_type = getattr(sublimeplugin, '%sCommands' % cmd_type)
      is_enabled = getattr(runner, 'canRunCommand', None)
      if not is_enabled: continue
      for cmd in cmds_of_type:
        if is_enabled(cmd):
          to_sort.append((cmd_type, cmds_of_type[cmd].__module__, cmd))

    to_sort.sort()

    window.showQuickPanel("", "executeNamedCommand", 
        [`(c[0], c[2])` for c in to_sort],
        ['\\'.join(c) for c in to_sort],
        sublime.QUICK_PANEL_FILES )

class ExecuteNamedCommandCommand(sublimeplugin.WindowCommand):
  def run(self, window, args):
    cmd_type, cmd = eval(args[0])
    cmd_runners(window)[cmd_type].runCommand(cmd)