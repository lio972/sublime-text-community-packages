#################################### IMPORTS ###################################

# Std Libs
import os
import sys

# Perforce Imports
# Prepend `lib.` to all import statements from examples
from lib.P4 import P4, P4Exception

# Sublime Modules
import sublime
import sublimeplugin

################################# DOCUMENTATION ################################
"""

See scripting_docs/p4script.pdf chapter 3 Python scripting

"""
################################################################################

class Perforce(sublimeplugin.TextCommand):
    def run(self, view, args):
        sublime.messageBox(`dir(P4)`)

################################################################################