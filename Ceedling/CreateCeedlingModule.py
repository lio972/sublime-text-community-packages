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


# import functools
# import threading
# import sublime

# def threaded(finish=None, msg="Thread already running"):
#     def decorator(func):
#         func.running = 0
#         @functools.wraps(func)
#         def threaded(*args, **kwargs):
#             def run():
#                 try:
#                     result = func(*args, **kwargs)
#                     if result is None:
#                         result = ()

#                     elif not isinstance(result, tuple):
#                         result = (result, )

#                     if finish:
#                         sublime.setTimeout (
#                             functools.partial(finish, args[0], *result), 0
#                         )
#                 finally:
#                     func.running = 0
#             if not func.running:
#                 func.running = 1
#                 threading.Thread(target=run).start()
#             else:
#                 sublime.statusMessage(msg)
#         threaded.func = func
#         return threaded
#     return decorator
    
# class SomeFuckingCommand(sublimeplugin.TextCommand):
#     def run(self, view, args):
#         # do some stuff
#         # call threaded func
#         self.some_fucking_function(arg)

#     def finished(self, processed):
#         sublime.statusMessage('Finished cunt')

#     @threaded(finish=finished, msg="Already running the fucking command!")
#     def some_fucking_function(self, arg):
#         return processed