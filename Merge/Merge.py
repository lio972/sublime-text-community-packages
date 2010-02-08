import sublime, sublimeplugin

import os
from subprocess import Popen


WINMERGE = '"%s\WinMerge\WinMergeU.exe"' % os.environ['ProgramFiles']

class MergeCommand(sublimeplugin.ApplicationCommand):
	def __init__(self):
		self.fileA = self.fileB = None
        
	def run(self, args):
		Popen('%s /e /ul /ur "%s" "%s"' % (WINMERGE, self.fileA, self.fileB))
	
	def onActivated(self, view):
		if view.fileName() != self.fileA:
			self.fileB = self.fileA
			self.fileA = view.fileName()