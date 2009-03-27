import sublime, sublimeplugin


class stripSelectionCommand(sublimeplugin.TextCommand):
	"""
	Removes leading and trailing whitespace from selections
	"""
	def run(self, view, args):
		rs = []
		for region in view.sel():
			s = view.substr(region)
			if(not s.strip()):
				# strip whitespace selections
				rs.append(sublime.Region(region.begin(),region.begin()))
				continue
			a, b = region.a, region.b
			if(b > a):
				a += len(s) - len(s.lstrip())
				b -= len(s) - len(s.rstrip())
			else: # selection is inverted, keep it that way
				b += len(s) - len(s.lstrip())
				a -= len(s) - len(s.rstrip())
			rs.append(sublime.Region(a,b))
		view.sel().clear()
		for region in rs:
			view.sel().add(region)
			
	def isEnabled(self, view, args):
		return view.hasNonEmptySelectionRegion();
