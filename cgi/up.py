#!/usr/bin/python -u

print "Content-type: text/plain\n\n"

import util, os, subprocess, cgi
import datetime, os, util
import cgitb
cgitb.enable()


revision = "unknown"
project  = "unknown"

form = cgi.FieldStorage()

if form.has_key('revision'):
  revision = form['revision'].value
  
if form.has_key('project'):
  project = form['project'].value
  
msg = "Updating project %s, revision %s, at %s\n" % (project, revision, datetime.datetime.now())
print msg

# log the update attempt.
log = os.path.join(util.site, 'svnlog.txt')
f = file(log, 'a')
f.write(msg)
f.close()

up = os.path.join(util.site, 'up')
print up
subprocess.call(up)
