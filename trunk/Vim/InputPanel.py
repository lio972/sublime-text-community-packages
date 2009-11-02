import sublime, sublimeplugin

# and type: view.runCommand('inputPanel')
class InputPanelCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		self.view = view
		view.window().showInputPanel(":", "", self.on_done, self.on_change, self.on_cancel)

	def on_done(self, input):
		self.parse(input)
	
	def on_change(self, input):
		pass

	def on_cancel(self):
		pass

	def parse(self, cmd):
		view = self.view
		if cmd == "w":
			view.window().runCommand('save')
		elif cmd == "wa":
			view.window().runCommand('saveAll') 
		elif cmd == "q":
			view.window().runCommand('hotExit')