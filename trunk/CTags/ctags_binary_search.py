################################################################################

# Std Libs
from __future__ import with_statement

import re
import bisect
import os
import array
import time
import itertools

import pprint
import ctags

################################################################################

first = re.compile(r'([^\t]+)\t')

################################################################################
    
def log_divides(f):
    f.accessed = 0
    def wrapped(self, i):
        item = f(self, i)
        f.accessed += 1
        print f.accessed, i
        return item
    return wrapped
    
class TagFile(object):
    lines_at = array.array('I')
    
    def __init__(self, p):
        self.p = p
    
    # @log_divides
    def __getitem__(self, index):
        self.fh.seek(index)
        self.fh.readline()
        return first.match(self.fh.readline()).group(1)

    def __len__(self):
        return os.stat(self.p)[6]

    def close(self):
        self.fh.close()

    def get(self, tag):
        with open(self.p) as self.fh:
            b4 = bisect.bisect_left(self, tag)
            self.fh.seek(b4)

            for l in self.fh:
                comp = cmp(first.match(l).group(1), tag)

                if   comp == -1: continue
                elif comp ==  1: break
                
                yield l                

    def get_tags_dict(self, tag):
        return ctags.parse_tag_lines(self.get(tag))
        
################################################################################
        
if __name__ == '__main__':
    if 0: raw_input = lambda s: s

    raw_input('About to use memory')

    t = time.time()
    b = TagFile(r'C://python25//lib//tags')
    print time.time() - t
    
    t = time.time()
    c = b.get_tags_dict('Test')
    print len(c['Test']), 'tags'
    print time.time() - t
    
    raw_input('Press enter to continue')
    
################################################################################