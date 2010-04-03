import subprocess, os, re, markdown

root = "/svn/sublime/sublime-text-community-packages/trunk"
site  = "/svn/sublime/sublime-text-community-packages"

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

def processMarkdown(content):
  content = rewriteWikiLinks(content)
  content = markdown.markdown(content)
  return content
  
def wikiLinkToNormal(match):
  name = match.groups(1)[0]
  clean = displayName(name)
  result = "[%s](%s.html)" % (clean,name)
  return result

def displayName(name):
  return name.replace('-', ' ')

def rewriteWikiLinks(content):
  linkre = re.compile(r'\(\@(.*?)\)')
  content = linkre.sub(wikiLinkToNormal, content)
  content = content.replace("\@","@")
  return content