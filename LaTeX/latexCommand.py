import sublime, sublimeplugin

# Insert LaTeX command based on current word
# Position cursor inside braces

class latexCommandCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		currword = view.word(view.sel()[0])
		command = view.substr(currword)
		view.erase(currword)
		snippet = "\\\\" + command + "{$1} $0"
		view.runCommand("insertInlineSnippet", [snippet])
