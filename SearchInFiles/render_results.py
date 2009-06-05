#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
from __future__ import with_statement

import os
import webbrowser

# 3rd Party Libs
from genshi.core import Stream
from genshi.output import encode, get_serializer
from genshi.template import Context, TemplateLoader

import sublime

TEMPLATES_PATH = os.path.join( sublime.packagesPath(), 
                               'SearchInFiles', 'templates')

#################################### LOADER ####################################

loader = TemplateLoader( 
    TEMPLATES_PATH, 
    auto_reload=True
)

################################################################################

def render(**kw):
    t = loader.load('results.html')
    
    ctxt = Context()
    ctxt.push(kw)
    
    serializer = get_serializer('xhtml')
    
    stream = t.generate(ctxt)
    
    return encode(serializer(stream), method=serializer,
                   encoding='utf8')            

def render_and_dump(**kw):
    f = os.path.join(TEMPLATES_PATH,  'temp.html')
    
    with open(f, 'w') as fh:
        fh.write(render(**kw))

    webbrowser.open(f)

################################################################################
