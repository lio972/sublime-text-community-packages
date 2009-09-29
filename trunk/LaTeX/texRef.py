import sublime, sublimeplugin, os, os.path, re

# References and citations

done = False

class TexRefCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		# get current point
		# assume no selection, or a singe selection (for now)
		currsel = view.sel()[0]
		point = currsel.b
		prefix = view.substr(view.word(point)).strip()
		print currsel, point, prefix,len(prefix)
		completions = []
		view.findAll('\\label\{([^\{]*)\}',0,'\\1',completions)
#		print completions
#		print "%d labels" % (len(completions),)
		# no prefix, or braces
		if not prefix in ["", "{}", "{", "}"]:
			fcompletions = [comp for comp in completions if prefix in comp]
		else:
			prefix = "" # in case it's {} or { or }
			fcompletions = completions
		# The drop-down completion menu contains at most 16 items, so
		# show selection panel if we have more.
		print prefix, len(fcompletions)
		if len(fcompletions) == 0:
			sublime.errorMessage("No references starting with %s!" % (prefix,))
			return
		if len(fcompletions) <= 16:
			view.showCompletions(point, prefix, fcompletions)
		else:
			def onSelect(i):
				# if we had an actual prefix, replace it with the label,
				# otherwise insert the label.
				# FIXME like TextMate, if you give e.g. thm:so as prefix
				# you may get thm:thm:something
				if prefix not in ["", "{}", "{", "}"]:
					view.replace(currword, fcompletions[i])
				else:
					view.insert(point, fcompletions[i])
			view.window().showSelectPanel(fcompletions, onSelect, None, 0)
		print "done"

