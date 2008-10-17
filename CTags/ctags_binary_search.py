################################################################################

# Std Libs
from __future__ import with_statement

import re
import bisect
import os
import time

import pprint
import ctags

################################################################################
    
def log_divides(f):
    f.accessed = 0
    def wrapped(self, i):
        item = f(self, i)
        f.accessed += 1
        print f.accessed, i
        return item
    return wrapped
    
SYMBOL = re.compile(r'([^\t]+)\t')
FILENAME = re.compile("[^\t]+\t([^\t]+)\t")

class TagFile(object):
    def __init__(self, p, field_re):
        self.p = p
        self.field_re = field_re
    
    # @log_divides
    def __getitem__(self, index):
        self.fh.seek(index)
        self.fh.readline()
        return self.field_re.match(self.fh.readline()).group(1)

    def __len__(self):
        return os.stat(self.p)[6]

    def close(self):
        self.fh.close()

    def get(self, tag):
        with open(self.p) as self.fh:
            b4 = bisect.bisect_left(self, tag)
            self.fh.seek(b4)

            for l in self.fh:
                comp = cmp(self.field_re.match(l).group(1), tag)

                if   comp == -1: continue
                elif comp ==  1: break
                
                yield l                

    def get_tags_dict(self, tag):
        return ctags.parse_tag_lines(self.get(tag))
        
################################################################################
        
if __name__ == '__main__':
    if 1: raw_input = lambda s: s

    raw_input('About to use memory')

    t = time.time()
    b = TagFile(
        r'C://python25//lib//tags_unsorted', field_re = FILENAME
    )
    
    print time.time() - t
    
    t = time.time()
    c = b.get_tags_dict(r'.\aifc.py')
    # print len(c[r'.\basic.c']), 'tags'

    for val in c.values():
        for d in val:
            print d['filename']

    # print c
    
    print time.time() - t
    
    
     
    raw_input('Press enter to continue')
    
################################################################################