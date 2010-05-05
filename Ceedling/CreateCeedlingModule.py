import sublime, sublimeplugin
import functools
import subprocess
import re

class CreateCeedlingModuleCommand(sublimeplugin.TextCommand):

    def run(self, view, args):
        window = view.window()
        current_file_path = view.fileName()
        
        # subpaths = re.split(r"[\\\/]", current_file_path)
        # print(subpaths)
        
        window.showInputPanel("Enter module path", current_file_path,
            functools.partial(self.onDone, view), None, None)
        
        cmd = "rake paths:source"
        p = subprocess.Popen(cmd, shell=True, bufsize=1024, stdout=subprocess.PIPE)
        p.wait()
        lines = p.stdout.read().split("\n - ")[1:]
        for line in lines:
            print(line)
            
    # def onChange(self, view, text):
        # todo: tab completion
                
    def onDone(self, view, text):
        window = view.window()
        sublime.statusMessage("Creating module: " + text)
        cmd = "rake module:create[" + text + "]"
        window.runCommand("exec", ["^(...*?):([0-9]*):?([0-9]*)", cmd])
        window.runCommand("scanProject")
        sublime.statusMessage("Created module: " + text)
