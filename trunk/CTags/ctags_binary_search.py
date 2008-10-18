################################################################################

# Std Libs
# from __future__ import with_statement

# import re
# import bisect
# import os
# import time

# import pprint
# import ctags

# from helpers import time_function

################################################################################
    
# def log_divides(f):
#     f.accessed = 0
#     def wrapped(self, i):
#         item = f(self, i)
#         f.accessed += 1
#         print f.accessed, i
#         return item
#     return wrapped
    
# SYMBOL = 0
# FILENAME = 1

# class TagFile(object):
#     def __init__(self, p, column):
#         self.p = p
#         self.column = column
    
#     @log_divides
#     def __getitem__(self, index):
#         self.fh.seek(index)
#         self.fh.readline()
#         return self.fh.readline().split('\t')[self.column]

#     def __len__(self):
#         return os.stat(self.p)[6]

#     def get(self, tag):
#         with open(self.p) as self.fh:
#             b4 = bisect.bisect_left(self, tag)
#             self.fh.seek(b4)

#             for l in self.fh:
#                 comp = cmp(l.split('\t')[self.column], tag)

#                 if   comp == -1: continue
#                 elif comp ==  1: break
                
#                 yield l                

#     def get_tags_dict(self, tag):
#         return ctags.parse_tag_lines(self.get(tag))

################################################################################

# if __name__ == '__main__':
    # pass
    
################################################################################