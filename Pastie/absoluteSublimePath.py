# coding: utf8

############################   UNICODE SYS.PATH   ##############################

from ctypes import windll, create_unicode_buffer, sizeof

import os, sys, sublime

def addSublimePackage2SysPath(unicodePath):
    """                    
    
    usage:
        
        # coding: utf8      
       
        # You must declare encoding on first or second line if using unicode
        
        addSublimePackage2SysPath( unicode('山科 氷魚', 'utf8') )
        
            or
        
        addSublimePackage2SysPath(u'RegexBuddy')
    
    """
    if not isinstance(unicodePath, unicode):
        raise Exception("'unicodePath' paramater must be unicode")
    
    unicodeFileName = os.path.join( sublime.packagesPath(), unicodePath )
            
    buf = create_unicode_buffer(512)
    if not windll.kernel32.GetShortPathNameW(unicodeFileName, buf, sizeof(buf)):
        
        sublime.messageBox (
      
          'There was an error getting 8.3 shortfile names for the packages. ' 
          'These are relied upon as python does not support unicode for its '
          'module paths. Make sure shortpath names are ENABLED and take steps '
          'to make sure they have been created before trying again.'
      
        )
        
        import webbrowser
        try: webbrowser.open('http://support.microsoft.com/kb/210638')
        except: pass
        
        raise Exception('Error with GetShortPathNameW')
    
    path = buf.value
    if path not in sys.path:    
        sys.path.append(buf.value)
    
    # Be sure not use relative import, as that is whole purpose of the function
    
    try: os.chdir('C:\\')
    except: pass
    
################################################################################