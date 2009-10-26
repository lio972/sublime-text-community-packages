import sublime, sublimeplugin

# To run it, save it within the User/ directory, then open the console (Ctrl+~),
# and type: view.runCommand('vim')

# ==========================================================================================
class SelectModeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		if args[0] == 'control':
			self.switch(view, True)
		elif args[0] == 'normal':
			self.switch(view, False)
			
	def switch(self, view, isCtrl):
		if isCtrl:
			print "entering Control mode"
			# set restore point
			view.runCommand('glueMarkedUndoGroups')
			# set special color scheme
			colorscheme = view.options().get('colorscheme')
			view.options().set('Vim.original_colorscheme', colorscheme)
			view.options().set('colorscheme', "Packages/Color Scheme - Default/Cobalt.tmTheme")			
		else:
			print "exiting Control mode"
			# set restore point
			view.runCommand('markUndoGroupsForGluing')			
			# set back normal color scheme
			colorscheme = view.options().get('Vim.original_colorscheme')
			view.options().set('colorscheme', colorscheme)	
			
		# set modes
		view.options().set('vimMode', isCtrl)
		view.options().set('commandMode', isCtrl)
		

# ==========================================================================================
class NormalModeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		print "entering normal mode"
		view.runCommand('selectMode normal')
				
				
# ==========================================================================================
class InsertModeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		print "entering insert mode"
		view.runCommand('selectMode normal')
		if len(args) > 0:
			if args[0] == 'bol':
				view.runCommand('moveTo bol')
			elif args[0] == 'eol':
				view.runCommand('moveTo eol')
			elif args[0] == 'append':
				view.runCommand('move characters 0')


# ==========================================================================================
class ControlModeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		print "starting Control Mode"
		view.runCommand('selectMode control')
		