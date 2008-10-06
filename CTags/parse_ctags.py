################################################################################
# coding: utf8
################################################################################

# Std Libs
from __future__ import with_statement

import re
import pprint
import unittest
import os

################################################################################

TAGS_RE = re.compile (

    '(?P<symbol>[^\t]+)\t'
    '(?P<filename>[^\t]+)\t'
    '(?P<ex_command>.*?);"\t'
    '(?P<type>[^\t]+)'
    '(?:\t(?P<fields>.*))?'
)

################################################################################

def parse_tag_file(tag_file):
    tags_lookup = {}

    with open(tag_file) as tags:
        for search_obj in (t for t in (TAGS_RE.search(l) for l in tags) if t):
            tag = post_process_tag(search_obj, tag_file)
            tags_lookup.setdefault(tag['symbol'], []).append(tag)

    return tags_lookup

def unescape_ex(ex):
    return re.sub(r"\\(\$|/|\^|\\)", r'\1', ex)
        
def process_ex_cmd(ex):
    return ex if ex.isdigit() else unescape_ex(ex[2:-2])

def post_process_tag(search_obj, tag_file):
    tag = search_obj.groupdict()

    fields = tag.get('fields')
    if fields:
        tag.update(process_fields(fields))

    tag['ex_command'] = process_ex_cmd(tag['ex_command'])

    return tag

def process_fields(fields):
    fields_dict = {}

    for f in fields.split('\t'):
        f = f.split(':')

        # These, if existing, are keys with no values... retarded
        for key in f[:-2]:
            fields_dict[key] = True # Essentially boolean?

        # The last two are actual key value pairs because separated by \t
        key, value =  f[-2:]
        fields_dict[key] = value

    return fields_dict

class Tag(object):
    "dot.syntatic sugar for tag dicts"
    def __init__(self, tag_dict):
        self.__dict__ = tag_dict

    def __repr__(self):
        return pprint.pformat(self.__dict__)

# - Parse an existing CTAGS file, and implement go-to-tag-under-cursor. CTAGS
# files can get quite large, so representing them efficiently should be a goal.
# Ideally, parsing should also be done in another thread, so the editor isn't
# blocked while reading in a multi-megabyte file. Getting this implemented
# nicely is a fair bit of work.

# Next step would be to automatically run exuberant ctags in the current
# directory, if there isn't a CTAGS file already, or then one that does exist is
# out of date.

# Once we're at a start where symbol definitions are in memory, there's a number
# of other things that can be done, such as listing them in the quick panel, and
# hooking them into auto-complete.

################################################################################

def dev_scribble():
    total_in_lookup = 0
    num_lines = len(open('tags').readlines())
    
    tags = parse_tag_file('tags')
    
    from itertools import groupby
    from operator import itemgetter as iget

    # for f, vals in groupby(tags.iteritems(), key=iget('filename')):
   
    for symbol, tag_list in tags.iteritems():
        # print '\n\n'
        
        pprint.pprint (dict (
            # (k, map(iget('ex_command'), v)) for (k,v) in
            (k, list(v)) for (k,v) in
            groupby(tag_list, iget('filename'))
        ))
        
        
        # for f, vals in :
        #     print f,
        #     grp = 
        #     if len(grp) > 1:
        #         print f, grp
                
    # for symbol, tag_list in tags.iteritems():
    #     for tag in tag_list:
    #         total_in_lookup += 1
    #         print Tag(tag)
    
    # print abs(num_lines - total_in_lookup) == 6 and 'OK' or 'FAILURE!'
    

class CTagsTest(unittest.TestCase):
    def test_all_search_strings_work(self):
        os.chdir(os.path.dirname(__file__))
        tags = parse_tag_file('tags')
        
        failures = []
        
        for symbol, tag_list in tags.iteritems():
            for tag in (Tag(t) for t in tag_list):
                if not tag.ex_command.isdigit():
                    with open(tag.filename) as fh:
                        file_str = fh.read()
                        if tag.ex_command not in file_str:
                            failures += [tag.ex_command]
        
        for f in failures:
            print f
               
        self.assertEqual(len(failures), 0, 'update tag files and try again')

if __name__ == '__main__':
    if 0: dev_scribble()
    else: unittest.main()

################################################################################
# TAG FILE FORMAT

# When not running in etags mode, each entry in the tag file consists of a
# separate line, each looking like this in the most general case:

# tag_name<TAB>file_name<TAB>ex_cmd;"<TAB>extension_fields

# The fields and separators of these lines are specified as follows:

# 1.
    
#     tag name

# 2.
    
#     single tab character

# 3.
    
#     name of the file in which the object associated with the tag is located

# 4.
    
#     single tab character

# 5.
    
#     EX command used to locate the tag within the file; generally a search
#     pattern (either /pattern/ or ?pattern?) or line number (see −−excmd). Tag
#     file format 2 (see −−format) extends this EX command under certain
#     circumstances to include a set of extension fields (described below)
#     embedded in an EX comment immediately appended to the EX command, which
#     leaves it backward-compatible with original vi(1) implementations.

# A few special tags are written into the tag file for internal purposes. These
# tags are composed in such a way that they always sort to the top of the file.
# Therefore, the first two characters of these tags are used a magic number to
# detect a tag file for purposes of determining whether a valid tag file is
# being overwritten rather than a source file. Note that the name of each source
# file will be recorded in the tag file exactly as it appears on the command
# line.

# Therefore, if the path you specified on the command line was relative to the
# current directory, then it will be recorded in that same manner in the tag
# file. See, however, the −−tag−relative option for how this behavior can be
# modified.

# Extension fields are tab-separated key-value pairs appended to the end of the
# EX command as a comment, as described above. These key value pairs appear in
# the general form "key:value". Their presence in the lines of the tag file are
# controlled by the −−fields option. The possible keys and the meaning of their
# values are as follows:

# access
    
#     Indicates the visibility of this class member, where value is specific to
#     the language.

# file
    
#     Indicates that the tag has file-limited visibility. This key has no
#     corresponding value.

# kind
    
#     Indicates the type, or kind, of tag. Its value is either one of the
#     corresponding one-letter flags described under the various −−<LANG>−kinds
#     options above, or a full name. It is permitted (and is, in fact, the
#     default) for the key portion of this field to be omitted. The optional
#     behaviors are controlled with the −−fields option.

# implementation

# When present, this indicates a limited implementation (abstract vs. concrete)
# of a routine or class, where value is specific to the language ("virtual" or
# "pure virtual" for C++; "abstract" for Java).

# inherits
    
#     When present, value. is a comma-separated list of classes from which this
#     class is derived (i.e. inherits from).

# signature
    
#     When present, value is a language-dependent representation of the
#     signature of a routine. A routine signature in its complete form specifies
#     the return type of a routine and its formal argument list. This extension
#     field is presently supported only for C-based languages and does not
#     include the return type.

# In addition, information on the scope of the tag definition may be available,
# with the key portion equal to some language-dependent construct name and its
# value the name declared for that construct in the program. This scope entry
# indicates the scope in which the tag was found. For example, a tag generated
# for a C structure member would have a scope looking like "struct:myStruct".