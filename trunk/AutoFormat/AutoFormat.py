import sublime, sublimeplugin
import os
import sys
import re


class AutoFormatCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		f = view.fileName();
		exe = sublime.packagesPath()
		exe = os.path.join(exe, "User")
		exe = os.path.join(exe, "AStyle.exe")
			
		# Spaces ion path workaround:
		# add an extra quote (!) before the quoted command name:
		# result = os.system('""pythonbugtest.exe" "test"')
		# Explanation:
		# there was a time when the cmd prompt treated all spaces as delimiters, so
		# >cd My Documents
		# would fail. Nowadays you can do that successfully and even
		# >cd My Documents\My Pictures
		# works.
		# In the old days, if a directory had a space, you had to enclose it in quotes
		# >cd "My Documents"
		# But you didn't actually need to include the trailing quote, so you could get away with
		# >cd "My Documents
		cmd = '""%(exe)s" "%(args)s""' % {'exe' : exe, 'args' : f } # stderr > out.txt 2>&1
		result = os.system(cmd)
		
		if not result:		
			s = open(f, 'r').read()
			region = sublime.Region(0L, view.size())
			view.replace(region, s)
		
	def isEnabled(self, view, args):
		lang = re.search(".*/([^/]*)\.tmLanguage$", view.options().getString("syntax")).group(1)
		lang = lang.lower()
		if lang == "c" or lang == "c++" or lang == "c#" or lang == "java":
			return True
		else:
			return False
