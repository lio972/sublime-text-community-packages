from pywinauto.application import Application

import time

[ u'C:\\python25\\python.exeCaptionButton_Floating_Window',
  u'C:\\python25\\python.exe', u'CaptionButton_Floating_Window',
  u'C:\\python25\\python.exeConsoleWindowClass', u'ConsoleWindowClass']

def launch_ipython():
    app = Application.start('python C:/python25/scripts/ipython.py D:/ipython/completion_server.py')
    return app['ConsoleWindowClass']