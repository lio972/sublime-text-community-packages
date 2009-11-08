import sublime, sublimeplugin

# To run it, save it within the User/ directory, then open the console (Ctrl+~),
# and type: view.runCommand('vim')

# ==========================================================================================
class SelectCtrlModeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		if args[0] == 'control':
			self.switch(view, True)
		elif args[0] == 'edit':
			self.switch(view, False)
			
	def switch(self, view, isCtrl):
		if isCtrl:
			# set restore point
			view.runCommand('glueMarkedUndoGroups')
			sublime.statusMessage("-- CTRL --")
			view.setStatus('Vim.status', '-- CTRL --')
		else:
			sublime.statusMessage("CTRL: OFF")
			# set restore point
			view.runCommand('markUndoGroupsForGluing')			
			view.eraseStatus('Vim.status')
			
		# set modes
		view.options().set('ctrlMode', isCtrl)
		view.options().set('commandMode', isCtrl)
		
		
# ==========================================================================================
class InsertModeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		view.runCommand('selectCtrlMode edit')
		if len(args) > 0:
			if args[0] == 'bol':
				view.runCommand('moveTo bol')
			elif args[0] == 'eol':
				view.runCommand('moveTo eol')
			elif args[0] == 'append':
				view.runCommand('move characters 0')


# ==========================================================================================
class CtrlModeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		if len(args) > 0:
			if args[0] == 'on':
				view.runCommand('selectCtrlMode control')
			elif args[0] == 'off':
				view.runCommand('selectCtrlMode edit')		
