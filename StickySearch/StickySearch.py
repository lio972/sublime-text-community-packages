import sublime, sublimeplugin

# To run it open the console (Ctrl+~),
# type: view.runCommand('stickySearch')
class StickySearchCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		# keep sticky per window (each window has its own set)
		key = "StickySearch_" + str(view.window().id())
		view.window().runCommand('findAllUnder')
		
		if 'add' in args:
			self.add(key, view)
		if 'clear' in args:
			self.clear(key, view)
		if 'set' in args:
			self.set(key, view)			
		
		self.clear_selection(view)

	def add(self, key, view):
		self.mark(key, view, view.getRegions(key))
	
	def set(self, key, view):
		self.mark(key, view, [])	
		
	def mark(self, key, view, regions):
		for s in view.sel():
			regions.append(sublime.Region(s.begin(), s.end()))
		view.addRegions(key, regions, "marker", sublime.PERSISTENT)

	def clear(self, key, view):
		view.eraseRegions(key)   

	def clear_selection(self, view):
		# create empty RegionSet object
		region_set = view.sel()
		region_set.clear()
		view.show(region_set)
