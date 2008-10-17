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

# class Tag(str):
#     def __eq__(self, other):
#         return FILENAME.match(self).group(1) == FILENAME.match(other).group(1)
        
#     def __lt__(self, other):
#         return  (
#             FILENAME.match(self).group(1) < FILENAME.match(other).group(1)
#         )

#     def __gt__(self, other):
#         return  (
#             FILENAME.match(self).group(1) > FILENAME.match(other).group(1)
#         )

################################################################################
        
if __name__ == '__main__':
    pass
    
################################################################################