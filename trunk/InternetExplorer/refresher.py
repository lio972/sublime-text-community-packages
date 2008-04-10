import sublime, sublimeplugin, webbrowser, time
from comtypes.client import CreateObject

# See MozLab, http://hyperstruct.net/projects/mozlab,
# from telnetlib import Telnet
# self.firefox = Telnet('localhost', 4242)
# self.firefox.write('BrowserReload()')

class InternetExplorerCommand(sublimeplugin.TextCommand):
    ie = None
    visible = False
    
    def readyIE(self):
        self.ie = CreateObject("InternetExplorer.Application")
    
    def run(self, view, args):
        try:
            if not self.ie:
                self.readyIE()
                self.ie.Navigate(view.fileName())
                self.ie.Visible = 1
                self.visible = 1
            
            else:
                self.ie.Visible = not self.ie.Visible
                self.visible = not self.visible
        except:
            self.ie = None
            self.run(view, args)
    
    def onPostSave(self, view):
        try:
            if self.visible:
                self.ie.Refresh()
        except: 
            pass