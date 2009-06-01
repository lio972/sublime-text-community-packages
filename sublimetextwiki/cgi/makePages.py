#!/usr/bin/python -u
import util, markdown

template = util.loadFile("../templates/page.template.html")

print template

for f in os.listdir('../pagesource'):
  print f
  #src = loadFile(f)
  #htm = markdown.markdown(src)
  #out = template % (f, f, htm)
  #util.saveFile()
  

