#!/usr/bin/env python
import util, markdown, os

template = util.templateContent("page.template.html")

srcdir = os.path.join(util.site, 'pagesource')

for f in os.listdir(srcdir):
  if f.endswith(".txt"):
    noext = f[:-4]
    fl = os.path.join(srcdir, f)
    src = util.loadFile(fl)
    print src
    src = util.rewriteWikiLinks(src)
    print src
    htm = markdown.markdown(src)
    out = template % (noext, noext, htm)
    ouf = os.path.join(util.site, 'pages', noext + '.html')
    util.saveFile(ouf, out)
    
