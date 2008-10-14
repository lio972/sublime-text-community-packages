################################################################################

import re
import unittest

################################################################################

SNIPPET_TEMPLATE = """
<snippet>
    <content><![CDATA[%s]]></content>
</snippet>
"""

BINDING_TEMPLATE = """
    <binding key="%s" command="insertSnippet %s">
        <context name="selector" value="%s"/>
    </binding>
"""

CONTEXTUAL_BINDING_TEMPLATE = """
    <binding key="tab" command="deleteTabTriggerAndInsertSnippet %s %s">
        <context name="selector"          value="%s"/>
        <context name="canUnpopSelection" value="false"/>
        <context name="allPreceedingText" value="%s"/>
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

INVALID_PATH_CHARS = map(chr,range(33) + [16,34,38,42,44,47,58,60,62,63,92,124])
INVALID_PATH_RE    = re.compile('|'.join(map(re.escape, INVALID_PATH_CHARS)))

SYNTAX_FILES = (
    ('Preferences', '*.tmPreferences'),
    ('Syntaxes',    '*.tmLanguage'),
    ('Syntaxes',    '*.plist'),
)

ASCII_PLIST_RE = re.compile(r'([A-Za-z0-9]+)\s*=\s*"(.*)";\s*$', re.M)

JUNK_RE = re.compile(r"<key>keyEquivalent</key>\s+<string>(\W+)</string>")

################################################################################

class TestBla(unittest.TestCase):
    def test_invalid_paths(self):
        pass

if __name__ == '__main__':
    unittest.main()