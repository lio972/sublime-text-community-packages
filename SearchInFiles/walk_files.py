################################################################################

import os
import re
import sys
from os.path import normpath, join, dirname, split, splitext, isabs

IGNORE = ( '.svn', '.git', '.bzr', '.jpg', '.gif', '.png', '.pyc', '.pyo', 
           '.bin', '.o', '.obj', '.lib', '.pdb', '.suo', '.ncb', '.dll', 
           '.exe', '.zip', '.tar', '.gz', '.bz2', '.tgz', '.pyd')

################################################################################

def find_files(wd, mask):
    split = mask.split(';')
    
    path = split[0]
    mask = re.compile(''.join(split[1:]))
    
    if isabs(path): wd = path
    else: wd = normpath(join(wd, path))
    
    # if 1: print wd, mask
    
    for dirpath, dirnames, filenames in os.walk(wd, topdown=True):
        for i in IGNORE:
            if i in dirnames:
                del dirnames[dirnames.index(i)]
        
        for i, f in enumerate(filenames):        
            if f.endswith(IGNORE):
                del filenames[i]

        for f in filenames:
            if mask.match(f):
                yield join(dirpath, f)
                
################################################################################

if __name__ == '__main__':
    for f in find_files(r'D:\portable_sync\APPDATA\SublimeText\Packages\\',
        './;.*' ):
        print f
    
################################################################################