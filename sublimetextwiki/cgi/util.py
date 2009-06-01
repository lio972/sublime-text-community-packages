import subprocess, os, re

root = "/homepages/25/d96254051/htdocs/sublime-subversion/trunk/"
site  = "/homepages/25/d96254051/htdocs/sublime"
linkre = re.compile('\(\@.*?\)')

def templateContent(filename):
  f = os.path.join(site, "templates", filename)
  return loadFile(f)

def saveFile(filename, content):
  f = open(filename, 'w')
  f.write(content)
  f.close()
  
def loadFile(filename):
  f = open(filename, 'r')
  content = f.read()
  return content
  
def run(args, cwd):
  print "Running '" + " ".join(args) + "'"
  print "cwd will be " + cwd
  subprocess.call(args, cwd=cwd)

def rewriteWikiLinks(content):
  return linkre.sub(content, "[$1]($1.html)"