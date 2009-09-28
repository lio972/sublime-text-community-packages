import sublime, sublimeplugin

# Insert LaTeX command based on current word
# Position cursor inside braces
# TODO: snippet-like jumping out with TAB

class latexCommandCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		currword = view.word(view.sel()[0])
		command = view.substr(currword)
		view.replace(currword, "\\" + command + "{}")
		view.runCommand("move characters -1")
