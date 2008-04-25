# coding: utf8

################################### IMPORTS ####################################

from absoluteSublimePath import addSublimePackage2SysPath

addSublimePackage2SysPath(u'RegexBuddy')

import os, sys, sublime, sublimeplugin, time, sys

from ctypes import windll
from comtypes.client import CreateObject, GetEvents, PumpEvents
from subprocess import Popen

################################## SETTINGS ####################################

POWERGREP = '"C:\\Program Files\\JGsoft\\PowerGREP3\\PowerGREP.exe"'

################################################################################

class PowerGrepCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        Popen(POWERGREP)

############################## ACTION TEMPLATE #################################

ACTION_TEMPLATE = [
        
3,          # 0: int  RegexBuddy Version number.  Must be set to 3. 
0,          # 1: int  Kind of action; 0 = match; 1 = replace; 2 = split. 

'',         # 2: BSTR The regular expression. 
'',         # 3: BSTR The replacement text.             

1,          # 4: BOOL Dot matches all. 
0,          # 5: BOOL Case insensitive. 
1,          # 6: BOOL ^ and $ match at line breaks. 
0,          # 7: BOOL Free-spacing syntax. 
1,          # 8: int  Split limit (if >= 2, the split array contains at most li
'python',   # 9: BSTR Regular expression flavor. 
            
            # One of: jgsoft, dotnet, java, perl, pcre, javascript, python, 
            # ruby, tcl, bre, ere, gnubre, gnuere, xml, xpath. 
            
'python',   # 10: BSTR Replacement text flavor. 

            # One of: jgsoft, dotnet, java, perl, javascript, python, ruby, tcl, 
            # phpereg, phppreg, realbasic, oracle, xpath. 
            
0,          # 11: int StringType. 

            # One of the values for the StringType parameter of the InitRegex 
            # function. If this value is nonzero, RegexBuddy will interpret 
            # elements 2 and 3 in this array using this string type. 
            
            # RegexBuddy will use the same value in FinishAction as you used in 
            # InitAction.
             
'sublime'   # 12: BSTR Description of the action. 

            # Used as the default description if the 
            # user adds the action to a library.                                                         
]

################################################################################

class RegexBuddyCommand(sublimeplugin.TextCommand):
    regexBuddy = None
    bufferCache = ('You need to initialize regexbuddy at least once outside the '
             'find panel to cache the view as a test string. File must be saved')
    
    def IRegexBuddyIntfEvents_FinishAction(self, this, Action):
        self.Action = Action[2]
    
    def launchRB(self):
        sublimeWH = windll.user32.GetForegroundWindow()        
        self.regexBuddy = CreateObject("RegexBuddy.RegexBuddyIntf3")
        self.regexBuddy.IndicateApp("Sublime Text", sublimeWH)
    
    def wait4Response(self, rbwh):
        # PumpEvents until action sent or regexbuddy no longer active window

        connection = GetEvents(self.regexBuddy, self)
        while not self.Action:
            PumpEvents(0.01)
            if windll.user32.GetForegroundWindow() != rbwh:
                break
    
    def initAction(self, action):
        self.regexBuddy.InitAction(action)
        
        rbwh = self.regexBuddy.GetWindowHandle()
        windll.user32.SetForegroundWindow(rbwh)
        
        return rbwh
    
    def updatePanel(self, view):
        view.erase(sublime.Region(0, view.size()))
        view.insert(0, self.Action)
    
    def updateView(self, view, selection):
        view.replace(selection, self.Action)
            
    def run(self, view, args):
        self.Action = None
        if not self.regexBuddy: self.launchRB()   
        
        viewBuffer = view.substr(sublime.Region(0, view.size()))
        selection = view.sel()[0]
        
        fn = view.fileName()
        inPanel = not fn and len(viewBuffer) < 100
        
        if inPanel: regex = viewBuffer
        else:
            regex = view.substr(selection)
            self.bufferCache = viewBuffer
            
        self.regexBuddy.SetTestString (
            self.bufferCache if inPanel else viewBuffer
        )
                            
        action = ACTION_TEMPLATE[:]
        action[2] = regex
        
        wh = self.initAction(action)
        self.wait4Response(wh)
        
        if self.Action:
            if inPanel: self.updatePanel(view)
            else: self.updateView(view, selection)