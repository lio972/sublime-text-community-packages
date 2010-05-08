# This plugin allows you to more easily manage pane focus and view location
# when in a multiple group (pane) layout
#
# args[0] value:    action
# ---------------------------------
#         move:		move the current view (buffer) to a different group (pane)
#		  focus:	makes a different group (pane) active
#
# args[1] value:    destination
# ---------------------------------
#        (default)  next group
#         right: 	next group
#         down:  	next group
#         next:  	next group
#         left:     previous group 
#         up:       previous group
#         previous: previous group

import sublime, sublimeplugin

class MoveToBufferCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		window = view.window()
		
		if args[1] == "left" or args[1] == "up" or args[1] == "previous":
			groupIdx = (window.activeGroup() - 1) % window.numGroups()
		else:
			groupIdx = (window.activeGroup() + 1) % window.numGroups()
			
		if args[0] == "move":
			window.setViewPosition(view, groupIdx, 100000) # moves to end of existing tabs
		else:
			window.focusView(window.activeViewInGroup(groupIdx))