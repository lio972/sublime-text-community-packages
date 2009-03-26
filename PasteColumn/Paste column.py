import sublime, sublimeplugin

class pasteColumnCommand(sublimeplugin.TextCommand):
	"""
	Use this command to cut and paste whole columns.
	
	If you had i.e. 10 selection cursors when cutting the column, you need 10
	selection cursors to paste the column.
	"""
	def run(self, view, args):
		clip = sublime.getClipboard().split(u"\n")
		for region in view.sel():
			view.replace(region, clip.pop(0))

	def isEnabled(self, view, args):
		return sublime.getClipboard() != ""
