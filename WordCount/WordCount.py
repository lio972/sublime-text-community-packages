import sublime, sublimeplugin, re

class wordCount(sublimeplugin.TextCommand):
	def run (self, view, args):
		content = view.substr(sublime.Region(0, view.size()))
		sublime.statusMessage("Word Count: %s in %s" % (self.count(content), view.fileName()))
		
	def count(self, content):
		# compress all whitespace to single spaces
		wrdRx = re.compile("\w")
		matchingWrd = False
		words = 0;
		for ch in content:
			isWrd = wrdRx.match(ch) != None
			if isWrd and not matchingWrd:
				# we're moving into a word from not-a-word
				words = words + 1
				matchingWrd = True
			if not isWrd:
				matchingWrd = False
		return words