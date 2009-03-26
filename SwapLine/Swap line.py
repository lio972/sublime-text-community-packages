import sublime, sublimeplugin


class swapLineCommand(sublimeplugin.TextCommand):
	"""
	Swaps the current line with the line before or the line after
	"""
	def run(self, view, args):
		if args[0] == "up":
			self.swapLineUp(view)
		elif args[0] == "down":
			self.swapLineDown(view)
		else:
			print "Wrong argument %s\n" % (args[0],)
	
	def swapLineUp(self, view):
		cursor = view.sel()[0].begin()
		(row, col) = view.rowcol(cursor)
		
		if row == 0:
			print "Can't move past first line"
			return
		
		lines = view.lines(sublime.Region(0, view.size()))

		previousLine = lines[row-1]
		currentLine = lines[row]
		
		newString = view.substr(currentLine) +"\n"+ view.substr(previousLine);
		wholeRegion = previousLine.cover(currentLine)
		
		view.replace(wholeRegion, newString)				
		
		view.runCommand("move lines -1")
		
	def swapLineDown(self, view):
		cursor = view.sel()[0].begin()
		(row, col) = view.rowcol(cursor)
		
		lines = view.lines(sublime.Region(0, view.size()))

		if row >= len(lines)-1:
			print "Can't move past last line"
			return

		currentLine = lines[row]
		nextLine = lines[row+1]
		
		newString = view.substr(nextLine) +"\n"+ view.substr(currentLine);
		wholeRegion = currentLine.cover(nextLine)
		
		view.replace(wholeRegion, newString)
						
	def isEnabled(self, view, args):
		"""
		Currently only enabled for a single selection
		"""
		return len(view.sel()) == 1