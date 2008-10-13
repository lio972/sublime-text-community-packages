###############################################################################

import re

###############################################################################
"""

All callables with prefix of filter_ will be applied to snippets

Callables will be passed 3 arguments:

    content     =>  The snippet content
    plist_dict  =>  The snippet plist as a python dict 
    bundle      =>  `xxxxx.tmBundle`

You can name the 3 variables whatever you like but they must be in that order

If no filtering is done just return None (implicit with no return)

"""

def filter_ruby_snippet_paren_rb(content, _, bundle):
    if bundle is 'Ruby.tmBundle':
        s = content.replace('`snippet_paren.rb end`', ')')
        return s.replace('`snippet_paren.rb`', '(')

###############################################################################