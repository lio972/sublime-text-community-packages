#!/usr/bin/python
import os

print 'Content-type: text/html\n\n'

#for direc in [d + "\n" for d in os.listdir(".") if os.path.isfile(d) and d.endswith(".sublime-package")]:
#  print direc

f = open("main.sublime-distro", 'r')
print f.read()
f.close()