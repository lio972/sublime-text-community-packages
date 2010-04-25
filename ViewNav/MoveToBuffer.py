import sublime, sublimeplugin

# This plugin allows you to more easily it will move the active view to the
# next/previous group.
#
# args[0] value: destination
#         right: 	next buffer
#         down:  	next buffer
#         next:  	next buffer
#         left:     previous buffer 
#         up:       previous buffer
#         previous: previous buffer
 
class MoveToBufferCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		window = view.window()
		if args[0] == "right" or args[0] == "down" or args[0] == "next":
			groupIdx = (window.activeGroup() + 1) % window.numGroups()
		else:
			groupIdx = (window.activeGroup() - 1) % window.numGroups()
		window.setViewPosition(view, groupIdx, 100000) # moves to end of existing tabs