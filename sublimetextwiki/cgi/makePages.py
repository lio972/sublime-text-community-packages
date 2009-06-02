#!/usr/bin/env python
import util, markdown, os, string
from string import Template

template = util.templateContent("page.template.html")

srcdir = os.path.join(util.site, 'pagesource')

for f in os.listdir(srcdir):
  if f.endswith(".txt"):
    noext = f[:-4]
    fl = os.path.join(srcdir, f)
    print "converting %s" % noext
    src = util.loadFile(fl)
    htm = util.processMarkdown(src)
    tpl = Template(template)
    ctx = dict(name=displayName(noext), content=htm)
    out = tpl.substitute(ctx)
    ouf = os.path.join(util.site, 'pages', noext + '.html')
    util.saveFile(ouf, out)
    
