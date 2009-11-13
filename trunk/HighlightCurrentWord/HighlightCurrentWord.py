import re
import sublime, sublimeplugin

import time
def print_timing(func):
	def wrapper(*arg):
		t1 = time.clock()
		res = func(*arg)
		t2 = time.clock()
	   	print '%s took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
		return res
	return wrapper
    
class HighlightCurrentWord(sublimeplugin.Plugin):
	# @print_timing
	def onSelectionModified(self, view):
		key = "HighlightCurrentWord"

		if len(view.sel()) != 1 or view.sel()[0].size() > 80 or view.options().getString("syntax") in [u"Packages/XML/XML.tmLanguage"]:
			# Skip: multiple selection, very large selections, XML files
			view.eraseRegions(key)
			return

		region = view.sel()[0]
		
		region = view.word(region) # COMMENT OUT IF TOO DISTRACTING
		
		currentWord = view.substr(region)#.strip(" \t\r\n<>[]{}|&*+-/\\,.?'\":;=()^%#@!~`")
		if re.match(r'^\w+$', currentWord):
			regions = view.findAll(r"\b\Q%s\E\b" % currentWord)
			# don't highlight word at cursor
			regions.remove(region)
			view.addRegions(key, regions, "comment")
		else:
			view.eraseRegions(key)

