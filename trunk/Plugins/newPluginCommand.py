from __future__ import with_statement

import sublime, sublimeplugin, os, sys, time
    
class NewPluginCommand(sublimeplugin.TextCommand):
    """
    
    NewPlugin command makes a new plugin dir and a keymap and .py file
    
    """
    
    def isEnabled(self, view, args):
        return args and len(args[0]) > 0
    
    def run(self, view, args):
        window = view.window()
        
        pluginName = args[1]
        camelName = pluginName[0].lower() + pluginName[1:] 
        
        pluginDir = os.path.join(sublime.packagesPath(), pluginName)

        try: os.mkdir(pluginDir)
        except: 
            sublime.errorMessage('Failed to make plugin dir %s' % pluginDir) 
            return
            
        keymapFile = os.path.join(pluginDir, 'Default.sublime-keymap')
        pluginFile = os.path.join(pluginDir, '%s.py' % pluginName)
        
        with open(pluginFile, 'w') as fh: pass
         
        with open(keymapFile, 'w') as fh: 
            fh.write("<bindings>\n<!-- 4 %s Package -->\n</bindings>" % pluginName)

        for f in (keymapFile, pluginFile): view.window().openFile(f)
        
        
        
################################################################################


IMPORTS = "import sublime, sublimeplugin${0:, os, sys}"

MAIN = """
class ${1:$PARAM1}Command(sublimeplugin.${3:Text}Command):
    %s $1 for $2 %s
    
    def isEnabled(self, ${4:view}, args):
        if 1:
            return True    
    
    def run(self, ${4:view}, args):
        ${5:print args}
        $6
""" % tuple(['"""']*2)

events = "onNew onClone onLoad onClose onPreSave onPostSave onModified onActivated" 

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
    
    Depending on the contents of the file inserts a snippet
    
    """
    
    def run(self, view, args):
        fn = view.fileName()
        buf = view.substr(sublime.Region(0, view.size()))

        snip = []
        
        if "import sublime" not in buf:
            snip.append(IMPORTS)
        
        snip.append(MAIN)
        
        # if not ['any' for event in events.split() if event in buf]:
        if 'class' not in buf: 
            snip.append(HANDLERS)
        
        if "__completions__" not in buf:
            snip.append(COMPLETIONS)
        
        snippet = "\n".join(snip)
                
        if fn:
            plugName = os.path.splitext(os.path.split(fn)[1])[0]
            plugName = plugName[0].upper() + plugName[1:]
        else:
            plugName = 'MyPlugin'
            
        view.runCommand('insertInlineSnippet', [snippet,  plugName])