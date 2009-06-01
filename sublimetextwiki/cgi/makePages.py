#!/usr/bin/env python
import util, markdown, os

template = util.templateContent("page.template.html")

srcdir = os.path.join(util.site, 'pagesource')

for f in os.listdir(srcdir):
  if f.endswith(".txt"):
    noext = f[:-4]
    fl = os.path.join(srcdir, f)
    print "converting %s" % noext
    src = util.loadFile(fl)
    src = util.rewriteWikiLinks(src)
    htm = markdown.markdown(src)
    nam = noext.replace('-', ' ')
    out = template % (nam, nam, htm)
    ouf = os.path.join(util.site, 'pages', noext + '.html')
    util.saveFile(ouf, out)
    
