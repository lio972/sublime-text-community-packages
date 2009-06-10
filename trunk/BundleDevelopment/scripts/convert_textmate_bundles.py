# coding: utf-8

################################################################################
# Std Libs

from __future__ import with_statement

import os
import sys
import glob
import pprint
import re
import string
import itertools
import inspect
import shutil

from os.path import join, normpath, dirname, basename, splitext, split

# 3rd Party Libs

# If you are running python 2.5 steal plistlib.py from $X/python26/Lib
import plistlib

# User Libs

from config import opt_parser
from constants import *
import snippet_filters

################################################################################

DEBUG = 1

################################################################################
# Helpers

class UniqueString(object):
    def __init__(self, joiner=''):
        self.joiner = joiner
        self.cache = []

    def __call__(self, result):
        if not result: return result

        if result in self.cache:
            for l in (`s` for s in xrange(1, 2 ** 16)):
                unique_result = result + self.joiner + l
                if unique_result not in self.cache:
                    self.cache.append(unique_result)
                    return unique_result
        else:
            self.cache.append(result)
            return result

def ensure_directory_exists(path):
    try: os.makedirs(path)
    except OSError: pass

def slug(s):
    # Remove bollix from filenames created by TM4Windows conversion script
    s = re.sub('%[a-fA-F0-9]{2}', '', s.strip().lower())
    
    # Sluggify
    s = re.sub('[^a-z0-9-]', '-', s)
    s = re.sub('-+', '-', s).strip('- ')
    
    return s or 'a'

def slug2(s):
    s = s.decode('utf-8')
    s = re.sub(' +', ' ', s.encode('ascii', 'ignore'))
    return valid_nt_path(s)

def valid_nt_path(path):
    "Removes all illegal characters from pathname and replaces with `-`"

    return re.sub('-+', '-', INVALID_PATH_RE.sub('-', path)).strip('- ')

def multi_glob(path, *globs):
    paths = []
    for g in globs: paths.extend( glob.glob(join(path, g)))
    return paths

def output_bundle_path(path):
    return path.endswith('.tmbundle') and path[:-9] or path 

################################################################################

def parse_malformed_snippet(snippet_text):
    match = JUNK_RE.search(snippet_text)
    
    if match:
        snippet_text = list(snippet_text)
        snippet_text[slice(*match.span())] = ['']
        
        return plistlib.readPlistFromString(''.join(snippet_text))

def parse_ascii_plist(plist):
    return dict(t.groups() for t in ASCII_PLIST_RE.finditer(plist))

def parse_snippets(path):
    "Generator, yields filename and plist dict for each snippet on `path`"

    snippet_files  = multi_glob(path, '*.tmSnippet', '*.plist')
    
    parsers = (
        plistlib.readPlistFromString, parse_ascii_plist, parse_malformed_snippet
    )

    for snippet_file in sorted(snippet_files):
        with open(snippet_file, 'r') as fh: snippet_text = fh.read()

        for parser in parsers:
            try:                    plist_dict = parser(snippet_text)
            except:                 continue

            if plist_dict:
                yield basename(snippet_file), plist_dict
                break

        if DEBUG and not plist_dict:
            print 'could not parse', snippet_file

snippet_filters = [
    m[1] for m in inspect.getmembers(snippet_filters)
    if m[0].startswith('filter_') and callable(m[1])
]

def convert_snippet(s, snippet_dict, bundle_name):
    for s_filter in snippet_filters:
        s = s_filter(s, snippet_dict, bundle_name) or s
        
        if s is snippet_filters.DONT_CONVERT:
            return s
    
    return s

################################################################################

def convert_tab_trigger(tab_trigger):
    """

    Convert TextMate tab trigger to sublime `x,y,z...,tab` form. Strips all non
    valid keybindings.

    >>> convert_tab_trigger('@atr')
    'a,t,r'

    """
    
    rebuilt = []

    for l in tab_trigger:
        if l.isalpha():                                rebuilt.append(l)
        elif l in BINDING_MAPPING:     rebuilt.append(BINDING_MAPPING[l])

    return ','.join(rebuilt)

def convert_contextual_tab_trigger(tab_trigger):
    return '\\b%s$' % re.escape(tab_trigger)

def convert_key_equivalent(key):
    if key:
        key = key.encode('utf-8')
        if all(t.isalpha() or t in HOTKEY_MAPPING for t in key):
            return '+'.join(HOTKEY_MAPPING.get(ch, ch) for ch in key)

################################################################################

def convert_textmate_snippets(bundle):
    unique_fname = UniqueString()

    if options.contextual: unique_contextual_trigger = UniqueString()
    else: unique_tab_trigger = UniqueString(',')

    ########################################################################

    snippets_dir = join(options.input, bundle, 'Snippets')
    
    if not os.path.exists(snippets_dir): return
    
    package_name = output_bundle_path(basename(split(snippets_dir)[0]))
    package_path = join(options.output, package_name)

    snippets = {}
    bindings = []

    ########################################################################

    for file_name, snippet_dict in parse_snippets(snippets_dir):
        tabTrigger    =    snippet_dict.get('tabTrigger',    '')
        keyEquivalent =    snippet_dict.get('keyEquivalent', '')
        content       =    snippet_dict.get('content')
        scope         =    snippet_dict.get('scope')

        ################################################################
        
        #TODO: CLEAN UP THIS CONVOLUTED MESS
        #      Make it create both bindings at the same time
        #      Extract a few functions
        
        if options.contextual:
            if tabTrigger:
                tabTrigger = unique_contextual_trigger(tabTrigger)
                tab_trigger =  convert_contextual_tab_trigger ( tabTrigger )
            else:
                tab_trigger = ''
        else:
            tab_trigger = (
                unique_tab_trigger(convert_tab_trigger(tabTrigger))
            )
            
            if tab_trigger: tab_trigger += ',tab'

        key_combo     =    convert_key_equivalent(keyEquivalent)

        binding = key_combo or (tab_trigger or
                 ("TODO_%s" % tabTrigger or keyEquivalent)
        )

        file_name = unique_fname(slug2(splitext(file_name)[0]))+'.sublime-snippet'

        ################################################################

        if binding and content:
            converted_snippet = convert_snippet (
                (SNIPPET_TEMPLATE % snippet_dict).encode('utf-8'), 
                snippet_dict, package_name
            )        
            
            if converted_snippet is snippet_filters.DONT_CONVERT:
                continue
            
            snippets[file_name] = converted_snippet
            
            snippet_path = '/'.join(['Packages', package_name, file_name])
            snippet_path = "'%s'" % snippet_path.replace("'", "\\'")
            
            if not key_combo and options.contextual:
                bindings.append ( 
                    CONTEXTUAL_BINDING_TEMPLATE % (
                        (`tabTrigger or 'TODO'`, snippet_path, scope, binding)
                    )
                )                
                
            else:
                bindings.append (
                    BINDING_TEMPLATE % (
                        binding, snippet_path, scope
                    )
                )

    ########################################################################

    if snippets:
        ensure_directory_exists(package_path)
        
        with open(join(package_path, 'Default.sublime-keymap'), 'w') as fh:
            fh.write (
                '<bindings>%s</bindings>' % ''.join(bindings)
            )

        for file_name, snippet in snippets.items():
            with open(join(package_path, file_name), 'w') as fh:
                fh.write(snippet)

def copy_syntax_files(bundle):
    src_path    = join(options.input, bundle)
    output_path = output_bundle_path(join(options.output, bundle))

    files = (glob.glob(join(src_path, *ftypes)) for ftypes in SYNTAX_FILES)
    files = list(itertools.chain(*files))

    if files:
        ensure_directory_exists(output_path)

        for src_file in (p.decode('utf-8') for p in files):
            dest = join(output_path, valid_nt_path(basename(src_file)))
            shutil.copy(src_file, dest)

def main():
    os.chdir(options.input)

    for bundle in glob.glob('*.tmbundle'):        
        if options.syntax: copy_syntax_files(bundle)
        convert_textmate_snippets(bundle)

    print 'Conversions complete'

def test():
    import doctest
    doctest.testmod(verbose=1)
    
if __name__ == '__main__':
    options, args = opt_parser.parse_args()
    (test if options.test else main)()