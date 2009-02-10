################################## IMPORTS #####################################

import sublime, sublimeplugin, sys, webbrowser, threading, os
from functools import partial

from absoluteSublimePath import addSublimePackage2SysPath

for egg in ("clientform-0.2.7-py2.5.egg", "mechanize-0.1.7b-py2.5.egg"):
    addSublimePackage2SysPath('Pastie', egg)

addSublimePackage2SysPath('Pastie')

from pidgin import activateApp

from mechanize import Browser

################################## SETTINGS ####################################

DEFAULT_SYNTAX = 'plain_text'
ENCODE_AS = 'utf8'

############################ IRC CLIENT SETTINGS ###############################

# Get window spy and get your irc clients toplevel window class and set a regex
# to match window title text, if sendKeysOnlyIfTextMatch matches and there are 
# sendKeys it will send them

# http://www.rutherfurd.net/python/sendkeys/ for SendKeys documentation

# Don't send a zillion pastes while setting up irc client activation

TESTING_IRC_CLIENT = 0

activateIrcClient = partial( activateApp,

                       windowClassMatch = "gdkWindowToplevel",
                  windowTitleTextMatch  = ".*",
                  windowTitleTextNot    = ".*?Buddy List.*?",
                
                sendKeysOnlyIfTextMatch = "^#",
                             sendKeys   = "^v" )
        
################################################################################        
                  
SYNTAXES = {}
SYNTAXES["Packages/C++/C.tmLanguage"] = "7"
SYNTAXES["Packages/CSS/CSS.tmLanguage"] = "8" 
SYNTAXES["Packages/Rails/HTML (Rails).tmLanguage"] = "12"
SYNTAXES["Packages/HTML/HTML.tmLanguage"] = "11"
SYNTAXES["Packages/Java/Java.tmLanguage"] = "9"
SYNTAXES["Packages/JavaScript/JavaScript.tmLanguage"] = "10"
SYNTAXES["Packages/PHP/PHP.tmLanguage"] = "15"
SYNTAXES["Packages/Text/Plain text.tmLanguage"] = "6"
SYNTAXES["Packages/Python/Python.tmLanguage"] =  "16"
SYNTAXES["Packages/Ruby/Ruby.tmLanguage"] =  "3"
SYNTAXES["Packages/Rails/Ruby on Rails.tmLanguage"] = "4"
SYNTAXES["Packages/SQL/SQL.tmLanguage"] = "14"
SYNTAXES["Packages/ShellScript/Shell-Unix-Generic.tmLanguage"] = "13"

# <option value="2">ActionScript</option>
# <option value="7">C/C++</option>
# <option value="8">CSS</option>
# <option value="5">Diff</option>
# <option value="12">HTML (ERB / Rails)</option>
# <option value="11">HTML / XML</option>
# <option value="9">Java</option>

# <option value="10">Javascript</option>
# <option value="1">Objective C/C++</option>
# <option value="17">Pascal</option>
# <option value="18">Perl</option>
# <option value="15">PHP</option>
# <option value="6">Plain text</option>
# <option value="16">Python</option>
# <option value="3">Ruby</option>
# <option value="4" selected="selected">Ruby (on Rails)</option>

# <option value="13">Shell Script (Bash)</option>
# <option value="14">SQL</option>
# <option value="19">YAML</option>

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
                
                form['paste[parser_id]'] = [lang]
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
        
        fn = view.fileName() 
        if fn and fn.endswith('.php'): 
            syntax = '15'
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