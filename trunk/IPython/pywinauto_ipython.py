from pywinauto.application import Application
from subprocess import list2cmdline
from os.path import join

import time

[ u'C:\\python25\\python.exeCaptionButton_Floating_Window',
  u'C:\\python25\\python.exe', u'CaptionButton_Floating_Window',
  u'C:\\python25\\python.exeConsoleWindowClass', u'ConsoleWindowClass']

def launch_ipython(completion_server):
    cmd_list = [
        'python', 
        'C:/python25/scripts/ipython.py',
        join(completion_server, 'completion_server.py')
    ]

    app = Application.start(list2cmdline(cmd_list))
    return app['ConsoleWindowClass']