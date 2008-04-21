# coding: utf8

############################   UNICODE SYS.PATH   ##############################

# This is to make sure that absolute paths set are unicode safe. 

from ctypes import windll, create_unicode_buffer, sizeof

import os, sys, sublime

def addSublimePackage2SysPath(unicodePath):
    unicodeFileName = os.path.join( sublime.packagesPath(), unicodePath )
            
    buf = create_unicode_buffer(512)
    if not windll.kernel32.GetShortPathNameW(unicodeFileName, buf, sizeof(buf)):
        raise Exception('Error with GetShortPathNameW')
    
    path = buf.value
    if path not in sys.path:    
        sys.path.append(buf.value)