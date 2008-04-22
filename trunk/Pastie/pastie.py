# REMEMBER TO DONATE TO PASTIE IF YOU USE THE SERVICE A LOT

import sublime, sublimeplugin, sys, webbrowser, pidgin, threading, os
from functools import partial

from absoluteSublimePath import addSublimePackage2SysPath

for egg in ("clientform-0.2.7-py2.5.egg", "mechanize-0.1.7b-py2.5.egg"):
    addSublimePackage2SysPath(packageName='Pastie', module=egg)

from mechanize import Browser 

DEFAULT_SYNTAX = 'plain_text'

syntax_map = {}
syntax_map["Packages/C++/C.tmLanguage"] = "c"
syntax_map["Packages/CSS/CSS.tmLanguage"] = "css" 
syntax_map["Packages/Rails/HTML (Rails).tmLanguage"] = "html_rails"
syntax_map["Packages/HTML/HTML.tmLanguage"] = "html"
syntax_map["Packages/Java/Java.tmLanguage"] = "java" 
syntax_map["Packages/JavaScript/JavaScript.tmLanguage"] = "javascript"
syntax_map["Packages/PHP/PHP.tmLanguage"] = "php"
syntax_map["Packages/Text/Plain text.tmLanguage"] = "plain_text"
syntax_map["Packages/Python/Python.tmLanguage"] =  "python"
syntax_map["Packages/Ruby/Ruby.tmLanguage"] =  "ruby"
syntax_map["Packages/Rails/Ruby on Rails.tmLanguage"] = "ruby_on_rails"
syntax_map["Packages/SQL/SQL.tmLanguage"] = "sql"
syntax_map["Packages/ShellScript/Shell-Unix-Generic.tmLanguage"] = "shell-unix-generic"


class PastieServiceCommand(sublimeplugin.TextCommand):
    working = False
    
    def pastie(self, input_text, lang='python', private = False):
        try:
            pastie = Browser()
            pastie.open(r'http://pastie.caboo.se/pastes/new')
            
            form = [x for x in pastie.forms()][1]
            
            form.set_all_readonly(False)    
            pastie.set_handle_robots(False)
            
            form['paste[parser]'] = [lang]
            form['paste[body]'] = input_text
            form['paste[authorization]'] = 'burger'
            
            if private:
                form.controls[1].selected = True
                form.controls[2]._value = '1'
            
            response = pastie.open(form.click())

            sublime.setTimeout( partial(self.finish, response.geturl()), 1)
        
        except Exception, e:
            sublime.setTimeout( partial(self.failed, e),  1)
                    
    def run(self, view, args):
        if self.working:
            sublime.statusMessage("Pastie already in progress! Be patient!")
            return
        
        sel = view.sel()[0]
        region = sublime.Region(0, view.size()) if sel.empty() else sel
        
        if view.fileName().endswith('.php'): 
            syntax = 'php'
        else: 
            syntax = syntax_map.get(view.options().get('syntax'), DEFAULT_SYNTAX)
        
        make_private = 'private' in args
        
        self.working = True
        threading.Thread(target = partial(
            self.pastie, view.substr(region), syntax, make_private)
        ).start()
        
        sublime.statusMessage("Pastie in progress")
            
    def finish(self, paste):
        sublime.setClipboard(paste)
        webbrowser.open(paste)
        
        #TODO: make setting for people to set own regex for window class/text
        #      use activateApp
        sublime.setTimeout(pidgin.activate_pidgin, 1000)
        
        # Make sure people don't send twice accidentally
        sublime.setTimeout(self.finished, 5000)
    
    def failed(self, exception):
        sublime.messageBox("Pastie failed:  \n\n%s" % exception)
        self.finished()
    
    def finished(self):
        self.working = False