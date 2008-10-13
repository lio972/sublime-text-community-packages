###############################################################################

import re

###############################################################################
"""

All callables with prefix of filter_ will be applied to snippets

Callables will be passed a snippet_string and a snippet_dict and bundle_name

If no filtering is done just return None (implicit with no return)


"""

def filter_ruby_snippet_paren_rb(snippet_string, snippet_dict, bundle_name):
    if 'Ruby' in bundle_name:
        s = snippet_string.replace('`snippet_paren.rb end`', ')')
        return s.replace('`snippet_paren.rb`', '('))

###############################################################################