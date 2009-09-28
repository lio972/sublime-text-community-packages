import sublime, sublimeplugin

# Insert LaTeX environment based on current word
# Position cursor inside environment
# TODO: snippet-like jumping out with TAB

class latexEnvironmentCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		currword = view.word(view.sel()[0])
		command = view.substr(currword)
		view.replace(currword, "\\begin{" + command + "}\n\n\\end{" + command + "}")
		view.runCommand("move lines -1")
