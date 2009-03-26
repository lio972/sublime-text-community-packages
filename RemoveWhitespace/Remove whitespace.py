import sublime, sublimeplugin, re
from functools import partial


class removeWhitespaceCommand(sublimeplugin.TextCommand):
	"""
	Blank lines and white space removal utilities
	"""
	def run(self, view, args):
		if('extra' in args):
			processRegion = partial(self.removeExtraBlankLines)
		elif('trailing' in args):
			processRegion = partial(self.removeTrailingWhitespace)
		else:
			processRegion = partial(self.removeBlankLines)
			
		if(len(view.sel()) == 1 and view.sel()[0].empty()):
			# nothing selected: process the entire file
			processRegion(view, sublime.Region(0L, view.size()))
		else:
			# process only selected regions
			for region in view.sel():
				processRegion(view, view.line(region))
		
	def isEnabled(self, view, args):
		return True
	
	def removeBlankLines(self, view, region):
		"""
		Remove every blank lines
		"""
		s = view.substr(region)
		out = u"\n".join([u for u in s.splitlines() if u.strip()])
		view.replace(region, out)

	def removeExtraBlankLines(self, view, region):
		"""
		Remove any extra blank line (i.e. leave at most 1 blank line)
		"""
		s = view.substr(region)
		p = re.compile(r"^([ \t]*\n)+", re.M)
		out = p.sub('\n', s)
		view.replace(region, out)

	def removeTrailingWhitespace(self, view, region):
		"""
		Remove trailing whitespace
		"""
		s = view.substr(region)
		out = u"\n".join([u.rstrip() for u in s.splitlines()])
		view.replace(region, out)