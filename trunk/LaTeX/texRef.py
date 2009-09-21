import sublime, sublimeplugin, os, os.path, re

# References and citations

class TexRefCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		print "entering texRef"
		# test only for now
		# get current point
		# assume no selection, or a singe selection (for now)
		currsel = view.sel()[0]
		point = currsel.b
		prefix = view.substr(view.word(point)).strip()
		print currsel, point, prefix,len(prefix)
		completions = []
		view.findAll('\\label\{(.*)\}',0,'\\1',completions)
		print completions
		if not prefix in ["", "{}"]:
			fcompletions = [comp for comp in completions if prefix in comp]
		else:
			prefix = "" # in case it's {}
			fcompletions = completions
		view.showCompletions(point, prefix, fcompletions)
		
		# def onSelect(i):
		# 	view.replace(currsel, "\\ref{" + fcompletions[i] + "}")
		
		# view.window().showSelectPanel(fcompletions, onSelect, None, 0)
		# print "done"