#!/usr/bin/python -u
import util, markdown

template = loadFile("../templates/page.template.html")

for f in os.listdir('../pages'):
  src = loadFile(f)
  htm = markdown.markdown(src)
  out = template % (f, f, htm)
  

