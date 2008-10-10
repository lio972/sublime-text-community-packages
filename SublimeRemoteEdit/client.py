################################################################################

# Std Libs
from __future__ import with_statement

import xmlrpclib
import sys

################################################################################

sublime = xmlrpclib.Server('http://localhost:8000')

args = sys.argv[1:]

if args:
    f = args[0]
    with open(f, 'r+w') as fh:
        edited = sublime.editBuffer(fh.read(), f)
        fh.seek(0)
        fh.write(edited)
else:
    edited_pipe = sublime.editBuffer(sys.stdin.read())
    print edited_pipe

################################################################################