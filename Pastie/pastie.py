################################## IMPORTS #####################################

import sublime, sublimeplugin, sys, webbrowser, threading, os
from functools import partial

from absoluteSublimePath import addSublimePackage2SysPath

for egg in ("clientform-0.2.7-py2.5.egg", "mechanize-0.1.7b-py2.5.egg"):
    addSublimePackage2SysPath(packageName='Pastie', module=egg)

addSublimePackage2SysPath(packageName='Pastie')

from pidgin import activateApp

from mechanize import Browser

################################## SETTINGS ####################################

DEFAULT_SYNTAX = 'plain_text'
ENCODE_AS = 'utf8'

# Don't send a zillion pastes while setting up irc client activation
TESTING_IRC_CLIENT = 0

############################ IRC CLIENT SETTINGS ###############################

# Get window spy and get your irc clients toplevel window class and set a regex
# to match window title text, if sendKeysOnlyIfTextMatch matches and there are 
# sendKeys it will send them

activateIrcClient = partial( activateApp,

                       windowClassMatch = "gdkWindowToplevel",
                  windowTitleTextMatch  = "(^#|.*?Serv|.*?freenode)",
                
                sendKeysOnlyIfTextMatch = "^#",
                             sendKeys   = "^v" )

#http://www.rutherfurd.net/python/sendkeys/ for SendKeys documentation
        
################################################################################        
                  
SYNTAXES = {}
SYNTAXES["Packages/C++/C.tmLanguage"] = "c"
SYNTAXES["Packages/CSS/CSS.tmLanguage"] = "css" 
SYNTAXES["Packages/Rails/HTML (Rails).tmLanguage"] = "html_rails"
SYNTAXES["Packages/HTML/HTML.tmLanguage"] = "html"
SYNTAXES["Packages/Java/Java.tmLanguage"] = "java"
SYNTAXES["Packages/JavaScript/JavaScript.tmLanguage"] = "javascript"
SYNTAXES["Packages/PHP/PHP.tmLanguage"] = "php"
SYNTAXES["Packages/Text/Plain text.tmLanguage"] = "plain_text"
SYNTAXES["Packages/Python/Python.tmLanguage"] =  "python"
SYNTAXES["Packages/Ruby/Ruby.tmLanguage"] =  "ruby"
SYNTAXES["Packages/Rails/Ruby on Rails.tmLanguage"] = "ruby_on_rails"
SYNTAXES["Packages/SQL/SQL.tmLanguage"] = "sql"
SYNTAXES["Packages/ShellScript/Shell-Unix-Generic.tmLanguage"] = "shell-unix-generic"

################################################################################


class PastieServiceCommand(sublimeplugin.TextCommand):
    working = False
    
    def pastie(self, input_text, lang='python', private = False):
        try:
            if not TESTING_IRC_CLIENT:    
                pastie = Browser()
                pastie.open(r'http://pastie.caboo.se/pastes/new')
                
                form = [x for x in pastie.forms()][1]
                
                form.set_all_readonly(False)    
                pastie.set_handle_robots(False)
                
                form['paste[parser]'] = [lang]
                form['paste[body]'] = input_text.encode(ENCODE_AS)
                form['paste[authorization]'] = 'burger'
                
                if private:
                    form.controls[1].selected = True
                    form.controls[2]._value = '1'
                
                response = pastie.open(form.click())
    
                url = response.geturl()
            else: 
                url = 'http://www.google.com.au' 
            
            sublime.setTimeout(partial(self.finish, url), 1)

        except Exception, e:
            import traceback
            
            sublime.setTimeout(partial(self.failed, traceback.format_exc(e)), 1)
                    
    def run(self, view, args):
        if self.working:
            sublime.statusMessage("Pastie already in progress! Be patient!")
            return
        
        sel = view.sel()[0]
        region = sublime.Region(0, view.size()) if sel.empty() else sel
        
        if view.fileName().endswith('.php'): 
            syntax = 'php'
        else: 
            syntax = SYNTAXES.get(view.options().get('syntax'), DEFAULT_SYNTAX)
        
        make_private = 'private' in args
        
        self.working = True
        threading.Thread(target = partial(
            self.pastie, view.substr(region), syntax, make_private)
        ).start()
        
        sublime.statusMessage("Pastie in progress")
            
    def finish(self, paste):
        sublime.setClipboard(paste)
        webbrowser.open(paste)

        sublime.setTimeout(activateIrcClient, 1000)
        
        # Make sure people don't send twice accidentally
        sublime.setTimeout(self.finished, 5000)
    
    def failed(self, exc):
        try:
            sublime.setClipboard(exc)
            
            sublime.messageBox (
                "Pastie failed (traceback on clipboard):  \n\n%s" % exc
            )
                        
        finally:
            self.finished()
    
    def finished(self):
        self.working = False