from __future__ import with_statement

import sublime, sublimeplugin

import os
from subprocess import Popen


WINMERGE = '"%s\WinMerge\WinMergeU.exe"' % os.environ['ProgramFiles']

class MergeCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		fileA = window.activeView().fileName()
		
		window.runCommand("nextViewInStack")
		fileB = window.activeView().fileName()
		window.runCommand("prevViewInStack")
		
		Popen('%s /e /ul /ur "%s" "%s"' % (WINMERGE, fileA, fileB))