import sublime, sublimeplugin

# and type: view.runCommand('deleteRange')
class DeleteRangeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		for command in " ".join(args).split(","):
			self.parse(view, command)
	
	def parse(self, view, command):
		if "lines 1" == command:
			view.runCommand('expandSelectionTo line')
			view.runCommand('leftDeleteCharacters')
	