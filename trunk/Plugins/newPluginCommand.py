from __future__ import with_statement

import sublime, sublimeplugin, os, sys, time, shutil

from os.path import split, join

from functools import partial
from collections import defaultdict
    
class NewPluginCommand(sublimeplugin.WindowCommand):
    callbacks = {}
    activationNumber = defaultdict(int)
    
    def run(self, window, args):
        # Get the plugins name
        
        pluginName = args[1]
        camelName = pluginName[0].lower() + pluginName[1:]
        
        pluginDir = join(sublime.packagesPath(), pluginName)
        
        # Make a directory to house the plugin and copy in commonly used Lib's
        
        try: os.makedirs(pluginDir)
        except: 
            sublime.errorMessage('Failed to make plugin dir %s' % pluginDir)
            return
            
        libs = join(sublime.packagesPath(), "Plugins\\Lib")
        os.popen('xcopy /e "%s" "%s"' % (libs, pluginDir))
            
        # Create the files

        keymapFile = join(pluginDir, 'Default.sublime-keymap')
        pluginFile = join(pluginDir, '%s.py' % pluginName)
        
        with open(pluginFile, 'w') as fh: fh.close()
        with open(keymapFile, 'w') as fh:
            fh.write("<bindings>\n<!-- 4 %s Package -->\n</bindings>" % pluginName)
            fh.close()

        # We want to automate inserting snippets with tab-stops but can not open
        # a file and then manipulate it's view so have to set a makeshift event
        # handler. When onActivated() if the fileName() is in the callbacks dict
        # then those callbacks (commands) will be run
        
        self.callbacks[pluginFile] = 'pluginSnippet'
        self.callbacks[keymapFile] = (
        
                "move lines 1;" * 2 + r"insertAndDecodeCharacters \n;" +\
                "move lines -1;" + r"insertAndDecodeCharacters \t;" +\
                "insertSnippet 'Packages/Plugins/newKeyMap.sublime-snippet' %s"\
                % camelName
        )
        
        #Open both the files, triggering onActivated event
        
        for f in (keymapFile, pluginFile):             
            window.openFile(f)
        
    def onActivated(self, view):
        if not self.callbacks: return
        
        fn = view.fileName()
        if fn in self.callbacks:
            
            # onActivated get's called twice and the first time it doesn't 
            # get proper access to the view and the ability to runCommand()
            # When we are finished we musst delete the callback from the dict 
            # so it's not called repeatedly. This is a workaround. 
            
            self.activationNumber[fn] += 1            
            if self.activationNumber[fn] == 2:
                for cmd in self.callbacks[fn].split(';'):
                    view.runCommand(cmd)
                
                # Tidy up
                del self.callbacks[fn]
            
            
################################################################################
################################################################################

# Snippet templates

IMPORTS = ( "import sublime, sublimeplugin${0:, os, sys}\n\n"
            "from absoluteSublimePath import addSublimePackage2SysPath\n"
            "#addSublimePackage2SysPath(u'%s')" )

MAIN = """
class ${1:$PARAM1}Command(sublimeplugin.${3:Text}Command):
    %s ${1:$PARAM1} for $2 %s
    
    def isEnabled(self, ${4:view}, args):
        if 1:
            return True    
    
    def run(self, ${4:view}, args):
        ${5:print args}
        $6
""" % tuple(['"""']*2)

EVENTS = "onNew onClone onLoad onClose onPreSave onPostSave onModified onActivated" 

HANDLERS = """
    # For reference only, remove all event handlers not in use
        
    def onNew(self, view):        
       %s Called when a new buffer is created. %s
       return
    
    def onClone(self, view):       
       %s Called when a view is cloned from an existing one. %s
       return
    
    def onLoad(self, view):       
       %s Called when the file is finished loading. %s
       return
    
    def onClose(self, view):      
       %s 
           Called when a view is closed (note, there may still be other views 
           into the same buffer). 
           
       %s
       
       return
    
    def onPreSave(self, view):       
       %s Called just before a view is saved. %s
       return
    
    def onPostSave(self, view):        
       %s Called after a view has been saved. %s
       return
    
    def onModified(self, view):    
       %s Called after changes have been made to a view. %s
       return
    
    def onActivated(self, view):        
       %s Called when a view gains input focus. %s
       return
    
""" % tuple(['"""']*16)

COMPLETIONS = """
__completions__ = %s

sublime setTimeout questionBox packagesPath getClipboard setClipboard
installedPackagesPath messageBox runCommand statusMessage errorMessage options
fileName options window size substr substr  insert erase replace sel line line
fullLine fullLine lines splitByLines  rowcol textPoint extractScope syntaxName
matchSelector clear add addAll  subtract contains begin end size empty cover
intersection intersects contains  contains newFile openFile activeView
getString set erase has 

%s 
""" % tuple(['"""']*2)

class PluginSnippetCommand(sublimeplugin.TextCommand):
    """ 
    
    Inserts a new plugin snippet thats contents depend on the current buffer.
    If buffer is essentially empty it will insert common imports and also insert
    all the event handlers for reference.
    
    """
    
    def run(self, view, args):
        fn = view.fileName()
        if fn:
            basePlugName = os.path.splitext(split(fn)[1])[0]
            plugName = basePlugName[0].upper() + basePlugName[1:]
        else:
            plugName = basePlugName = 'MyPlugin'
        
        buffer = view.substr(sublime.Region(0, view.size()))
        snip = []
        
        # Build the snippet based on what's arleady in the buffer. Don't need 
        # imports if they are already there.
        
        if "import sublime" not in buffer: snip.append(IMPORTS % basePlugName)

        # Always wan't a new class MyPlugin.....
        snip.append(MAIN)

        if 'class' not in buffer: 
            snip.append(HANDLERS)
            snip.append(COMPLETIONS)
            
        view.runCommand('insertInlineSnippet', ["\n".join(snip),  plugName])