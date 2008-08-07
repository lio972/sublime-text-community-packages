import sublime, sublimeplugin, re

class wordCount(sublimeplugin.TextCommand):
	def run (self, view, args):
		sels = view.sel()
		if len(sels) == 1 and sels[0].begin() == sels[0].end():
			# count whole document
			content = view.substr(sublime.Region(0, view.size()))
			sublime.statusMessage("Word Count: %s in %s" % (self.count(content), view.fileName()))
		else:
			# count sum of words in all selections
			regions = [view.substr(sublime.Region(s.begin(), s.end())) for s in sels]
			lens = [len(reg) for reg in regions]
			counts = [self.count(region) for region in regions]
			sublime.statusMessage("Word Count: %s in region(s) of %s" % (sum(counts), view.fileName()))

			
	def count(self, content):
		"""counts by counting all the start-of-word characters"""
	
		# regex to find word characters
		wrdRx = re.compile("\w")
		matchingWrd = False
		words = 0;
		for ch in content:
			# test if this char is a word char
			isWrd = wrdRx.match(ch) != None
			
			if isWrd and not matchingWrd:
				# we're moving into a word from not-a-word
				words = words + 1
				matchingWrd = True
			if not isWrd:
				# go back to not matching words
				matchingWrd = False
		return words