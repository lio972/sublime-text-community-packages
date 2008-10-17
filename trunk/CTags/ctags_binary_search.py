################################################################################

from __future__ import with_statement

import re
import bisect
import os
import array
import time
import itertools

################################################################################

first = re.compile(r'([^\t]+)\t')

################################################################################
    
class TagFile(object):
    lines_at = array.array('I', [0])
    
    def __init__(self, p):
        self.p = p
        
        self.fh = open(p, 'rb')
    
        position = 0
        for l in self.fh:
            self.lines_at.append(position)
            position += len(l)
    
    def __getitem__(self, index):
        pos = self.lines_at[bisect.bisect_left(self.lines_at, index)-1]
        self.fh.seek(pos)
        return first.match(self.fh.readline()).group(1)

    def __len__(self):
        return os.stat(self.p)[6]

    def close(self):
        self.fh.close()

    def get(self, tag):
        pos = bisect.bisect_left(self, tag)
        self.fh.seek(pos-1)

        for l in self.fh:
            if re.match('%s\t' % tag, l): yield l
            else: break

################################################################################
        
if __name__ == '__main__':
    raw_input('About to use memory')

    t = time.time()

    b = TagFile(r'C://python25//lib//tags')
    
    print time.time() - t
    
    t = time.time()
    for i, tag in enumerate(b.get('Tests')):
        print '%s:\n%s ' % (i, tag.strip())
    
    print time.time() - t
    
    raw_input('Press enter to continue')
    
################################################################################