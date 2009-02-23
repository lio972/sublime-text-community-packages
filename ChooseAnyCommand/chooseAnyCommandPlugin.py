#
# Choose Any Command -- lets you choose any runnable command.
# 
import sublime, sublimeplugin, os

#
# Provides the quickpanel entry for the command;
#
# commands = the dictionary of commands (text, window, app)
# cmd = the name of the command
# typ = a string representing the command type
#
def cmdinfo(commands, cmd, typ):
  return typ + "\\" + commands[cmd].__module__ + "\\" + cmd # + " " + " - ".join(dir(cmd))

#
# shows the QuickPanel with every runnable command available to Sublime Text.
#
class ChooseAnyCommandCommand(sublimeplugin.WindowCommand):
  
  def run(self, window, args):
    
    textCommandNames = sublimeplugin.textCommands.keys()
    windowCommandNames = sublimeplugin.windowCommands.keys()
    appCommandNames = sublimeplugin.applicationCommands.keys()

    textCommandNames.sort()
    windowCommandNames.sort()
    appCommandNames.sort()
    
    textCommands = [cmd for cmd in textCommandNames if window.activeView().canRunCommand(cmd)]
    windowCommands = [cmd for cmd in windowCommandNames if window.canRunCommand(cmd)]
    appCommands = [cmd for cmd in appCommandNames if sublime.canRunCommand(cmd)] 

    textNames = ["text\\" + cmd for cmd in textCommands]
    appNames = ["application\\" + cmd for cmd in appCommands]
    wndNames = ["window\\" + cmd for cmd in windowCommands]
    
    displayTextNames = [cmdinfo(sublimeplugin.textCommands, cmd, "text") for cmd in textCommands]
    displayAppNames = [cmdinfo(sublimeplugin.applicationCommands, cmd, "application") for cmd in appCommands]
    displayWndNames = [cmdinfo(sublimeplugin.windowCommands, cmd, "window") for cmd in windowCommands]
    
    display = displayTextNames + displayAppNames + displayWndNames
    cmds = textNames + appNames + wndNames
    
    window.showQuickPanel("", "executeNamedCommand", cmds, display, sublime.QUICK_PANEL_FILES)
    
class ExecuteNamedCommandCommand(sublimeplugin.WindowCommand):
  def run(self, window, args):    
    typeAndCmd = args[0].split("\\")
    typ = typeAndCmd[0]
    cmd = typeAndCmd[1]
    
    if typ=="text":
      window.activeView().runCommand(cmd)
    elif typ=="application":
      sublime.runCommand(cmd)
    elif typ=="window":
      window.runCommand(cmd)
