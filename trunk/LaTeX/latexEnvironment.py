import sublime, sublimeplugin

# Insert LaTeX environment based on current word
# Position cursor inside environment
# TODO: snippet-like jumping out with TAB

class latexEnvironmentCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		currword = view.word(view.sel()[0])
		command = view.substr(currword)
		view.erase(currword)
		snippet = "\\\\begin{" + command + "}\n$1\n\\\\end{" + command + "}$0"
		view.runCommand("insertInlineSnippet", [snippet])
