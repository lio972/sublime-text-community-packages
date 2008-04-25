# coding: utf8

############################   UNICODE SYS.PATH   ##############################

from ctypes import windll, create_unicode_buffer

import os, sys, sublime

def addSublimePackage2SysPath(packageName='', module=''):
    """                    
    
    usage:
        
        # coding: utf8      
       
        # You must declare encoding on first or second line if using unicode
        
        addSublimePackage2SysPath( unicode('山科 氷魚', 'utf8') )
        
            or
        
        addSublimePackage2SysPath(u'RegexBuddy')

    
    """
        
    unicodeFileName = os.path.join ( 
    
        sublime.packagesPath(), packageName, "Lib", module
    
    ).rstrip('\\')  #Just in case there is no module
        
            
    buf = create_unicode_buffer(512)
    if not windll.kernel32.GetShortPathNameW(unicodeFileName, buf, len(buf)):
        
        sublime.messageBox (

          'There was an error getting 8.3 shortfile names for %s package. ' 
          'These are relied upon as python does not support unicode for its '
          'module paths. Make sure shortpath names are ENABLED and take steps '
          'to make sure they have been created before trying again.' % packageName
        )
        
        import webbrowser
        try: webbrowser.open('http://support.microsoft.com/kb/210638')
        except: pass
        
        raise Exception('Error with GetShortPathNameW')
    
    path = buf.value.encode('ascii')
    if path not in sys.path:
        sys.path.insert(1, path)
        
################################################################################