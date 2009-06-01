#!/usr/bin/python -u

print "Content-type: text/plain\n\n"

import util, os, subprocess
up = os.path.join(util.site, 'up')
print up
subprocess.call(up)
#util.run([up], util.site)