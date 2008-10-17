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
        with open(self.p, 'rb') as self.fh:
            pos = bisect.bisect(self, tag)
            b4 = bisect.bisect_left(self, tag, 0, pos)

            self.fh.seek(b4)
    
            found = 0
            tag_first_letter = tag[0]
            
            for i, l in enumerate(self.fh):
                m = re.match('%s\t' % tag, l)
                if not found and not m and l.startswith(tag_first_letter): 
                    continue
                elif m:
                    found = 1 
                    yield l
                else: break


    def get_tags_dict(self, tag):
        return ctags.parse_tag_lines(self.get(tag))
        
################################################################################
        
if __name__ == '__main__':
    # raw_input = lambda s: s

    raw_input('About to use memory')

    t = time.time()

    b = TagFile(r'C://python25//lib//tags')
    
    print time.time() - t
    
    t = time.time()
    pprint.pprint(b.get_tags_dict('Tests'))
    print time.time() - t
    
    
    raw_input('Press enter to continue')
    
################################################################################