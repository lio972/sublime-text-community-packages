#
# Choose Any Command -- lets you choose any runnable command.
# 
import sublime, sublimeplugin

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
    
    cmds = textCommands + appCommands + windowCommands
    names = textNames + appNames + wndNames
    
    window.showQuickPanel("", "executeNamedCommand", names, sublime.QUICK_PANEL_FILES)
    
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
