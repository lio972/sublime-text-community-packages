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
import shutil
import optparse

from os.path import join, normpath, dirname, basename, splitext, split

# 3rd Party Libs

# If you are running python 2.5 steal plistlib.py from $X/python26/Lib
import plistlib

################################################################################
# Options

OUTPUT_PACKAGES_PATH = ur'E:\Sublime\sublime-text-community-packages\ConvertedTextMateSnippets'

TM_BUNDLES_PATH = "E:\\Sublime\\tmbundles4win\\Bundles\\"

# OUTPUT_PACKAGES_PATH = ur'/home/user/converted-textmate-snippets'

# TM_BUNDLES_PATH = "/home/user/Desktop/TextMate/trunk/Bundles"

DEBUG = 1

################################################################################
# Cmd Line Option Parser

opt_parser = optparse.OptionParser()

opt_parser.add_option (
     "-i",  "--input", metavar = "DIR",
     help   = "TextMate bundles path (containing *.tmbundle)",
     default =  TM_BUNDLES_PATH )

opt_parser.add_option (
     "-o",  "--output", metavar = "DIR",
     help    = "TextMate bundles path (containing *.tmbundle)",
     default = OUTPUT_PACKAGES_PATH )

opt_parser.add_option (
     "-t",  "--test", action = 'store_true',
     help   = "run tests" )

################################################################################
# Constants

SNIPPET_TEMPLATE = """
<snippet>
    <content><![CDATA[%s]]></content>
</snippet>
"""

BINDING_TEMPLATE = """
    <binding key="%s" command="insertSnippet 'Packages/%s/%s'">
        <context name="selector" value="%s"/>
    </binding>
"""

BINDING_MAPPING =   {
'`'     :     "backquote",
'\\'    :     "backslash",
','     :     "comma",
'='     :     "equals",
'['     :     "leftbracket",
'-'     :     "minus",
'.'     :     "period",
'"'     :     "quote",
']'     :     "rightbracket",
';'     :     "semicolon",
'/'     :     "slash",
' '     :     "space",
}

KNOWN_SUPPORTED_TM_VARIABLES = (
    "TM_CURRENT_LINE",
    "TM_CURRENT_WORD",
    "TM_FULLNAME",
    "TM_LINE_INDEX",
    "TM_LINE_NUMBER",
    "TM_SELECTED_TEXT",
    "TM_TAB_SIZE",
    "TM_FILENAME",
    "TM_FILEPATH",
)

HOTKEY_MAPPING = {
    "$" : "shift",
    "~" : "alt",                   
    "@" : "ctrl"
}

INVALID_PATH_CHARS = map(chr, [0,9,10,11,12,13,32,38,34,42,44,58,60,62,63,16])
INVALID_PATH_RE    = re.compile('|'.join(map(re.escape, INVALID_PATH_CHARS)))

SYNTAX_FILES = (
    ('Preferences', '*.tmPreferences'),
    ('Syntaxes',    '*.tmLanguage'),
    ('Syntaxes',    '*.plist'),
)

ASCII_PLIST_RE = re.compile(r'([A-Za-z0-9]+)\s*=\s*"(.*)";\s*$', re.M)

################################################################################
# Helpers

class UniqueString(object):
    def __init__(self, joiner=''):
        self.joiner = joiner
        self.cache = []

    def __call__(self, result):
        if not result: return

        if result in self.cache:
            for l in string.ascii_letters:
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

def valid_nt_path(path):
    "Removes all illegal characters from pathname and replaces with `-`"

    return re.sub('-+', '-', INVALID_PATH_RE.sub('-', path)).strip('- ')

################################################################################

JUNK_RE = re.compile(r"<key>keyEquivalent</key>\s+<string>(\W+)</string>")

def clean_malformed_snippet(snippet_text):
    match = JUNK_RE.search(snippet_text)
    
    if match:
        snippet_text = list(snippet_text)
        snippet_text[slice(*match.span())] = ['']
        
        return plistlib.readPlistFromString(''.join(snippet_text))

def parse_ascii_list(plist):
    return dict(t.groups() for t in ASCII_PLIST_RE.finditer(plist))

def multi_glob(path, *globs):
    paths = []
    [paths.extend( glob.glob(join(path, g))) for g in globs]
    return paths

def parse_snippets(path):
    "Generator, yields filename and plist dict for each snippet on `path`"

    snippet_files  = multi_glob(path, '*.tmSnippet', '*.plist')
    
    parsers = (
        plistlib.readPlistFromString, parse_ascii_list, clean_malformed_snippet
    )

    for snippet_file in snippet_files:
        with open(snippet_file, 'r') as fh: snippet_text = fh.read()

        for parser in parsers:
            try:                    plist_dict = parser(snippet_text)
            except:                 continue

            if plist_dict:
                yield basename(snippet_file), plist_dict
                break

        if DEBUG and not plist_dict:
            print 'could not parse', snippet_file
            
def convert_last_tabstops(snippet):
    """
    
    $0 placeholder used to denote `last` tabstop in TM. In Sublime the last
    tabstop is the highest one.

    """
    s = re.sub(r"(?:\$\{|\$)0", lambda l: l.group(0).replace('0', '15'), snippet)
    return s

def convert_snippet(snippet):
    s = convert_last_tabstops(snippet)

    # Transformations
    # s = re.sub(r"\$\{([0-9]{1,2})/.*?/\}", '$\\1', s)

    # Interpolated Shell Code
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

def convert_key_equivalent(key):
    if key:
        key = key.encode('utf-8')
        if all(t.isalpha() or t in HOTKEY_MAPPING for t in key):
            return '+'.join(HOTKEY_MAPPING.get(ch, ch) for ch in key)

################################################################################

def convert_textmate_snippets(bundle):
    unique_fname = UniqueString()
    unique_tab_trigger = UniqueString(',')

    snippets_dir = join(options.input, bundle, 'Snippets')
    
    if not os.path.exists(snippets_dir): return
    
    package_name = basename(split(snippets_dir)[0])
    package_path = join(options.output, package_name)

    snippets = {}
    bindings = []

    for file_name, snippet_dict in parse_snippets(snippets_dir):
        tabTrigger    =    snippet_dict.get('tabTrigger',    '')
        keyEquivalent =    snippet_dict.get('keyEquivalent', '')
        content       =    snippet_dict.get('content')
        scope         =    snippet_dict.get('scope')

        tab_trigger   =    unique_tab_trigger(convert_tab_trigger(tabTrigger))
        key_combo     =    convert_key_equivalent(keyEquivalent)

        binding = key_combo or ((tab_trigger and tab_trigger + ",tab") or
                 "TODO[%s]" % tabTrigger or keyEquivalent
        )

        file_name = unique_fname(slug(splitext(file_name)[0]))+'.sublime-snippet'

        if binding and content:
            snippets[file_name] = SNIPPET_TEMPLATE % content.encode('utf-8')
            bindings.append(
                BINDING_TEMPLATE % (binding, package_name, file_name, scope)
            )

    if snippets:
        ensure_directory_exists(package_path)
        
        with open(join(package_path, 'Default.sublime-keymap'), 'w') as fh:
            fh.write (
                '<bindings>%s</bindings>' % ''.join(bindings)
            )

        for file_name, snippet in snippets.items():
            with open(join(package_path, file_name), 'w') as fh:
                fh.write(convert_snippet(snippet))

def copy_syntax_files(bundle):
    src_path    = join(options.input, bundle)
    output_path = join(options.output, bundle)

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
        convert_textmate_snippets(bundle)
        copy_syntax_files(bundle)

    print 'Conversions complete'

def test():
    import doctest
    doctest.testmod(verbose=1)
    
    print 'Tests complete'
    
if __name__ == '__main__':
    options, args = opt_parser.parse_args()
    (test if options.test else main)()