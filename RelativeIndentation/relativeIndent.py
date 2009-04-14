#################################### IMPORTS ###################################

import sublime, sublimeplugin, re, os

import textwrap

############################### COMMON FUNCTIONS ###############################

def stripPreceding(selection, padding="", rstrip=True):
	"Strips preceding common space so only relative indentation remains"
	
	preceding_whitespace = re.compile("^(?:(\s*?)\S)?")
	common_start = len(selection)

	split = selection.split("\n")
	for line in (l for l in split if l.strip()):
		for match in preceding_whitespace.finditer(line):
			common_start = min(match.span(1)[1], common_start)
			if common_start == 0: break

	stripped = "\n".join( [split[0][common_start:]]  +
					   [padding + l[common_start:] for l in split[1:]] )
	
	return  stripped.rstrip("\n") if rstrip else stripped

def linesGetFirstsDisplacement(view, region):
	"""
	
	Expands a selection to encompass the lines it is situated in. 
	It then contracts the start point to where the first non space 
	character is found. Returns the start pt of the expanded 
	selection, displacement( characters to contracted selection), 
	and then the end pt.
	
	"""
	
	region = view.line(region)
	start, end = region.begin(), region.end()   
	displace = 0
	for x in xrange(start, end):
		if view.substr(x).isspace():
			displace += 1
		else: break
	return start, end, displace

def linesFirstNoPrecedingSpace(view, region, returnDisplace=False):
	"""
	
	Expands a selection to encompass the lines it is situated in.
	It then contracts the start point to where the first non space
	character is found. Returns a region
	
	"""
	
	start, end, displace = linesGetFirstsDisplacement(view, region)
	return sublime.Region(start+displace, end)
	
def getTab(view):
	"""
	
	Gets a series of empty space characters of size 'tabSize', the 
	current views setting for size of tab
	
	"""
	
	return view.options().get('tabSize') * " "

def substrStripPrecedingCommonSpace(view, region, padSecondary=""):
	"""
	
	Takes a view, and a Region of it, strips preceding common space 
	so only relative indentation remains
	
	"""
	
	region = view.line(region)
	tab = getTab(view)
	sel = view.substr(region).replace("\t", tab)
	return stripPreceding(sel, padding = padSecondary or tab)   

def eraseSelectionLines(view):
	"Erases any line with any selection, even if empty"
	for sel in view.sel(): view.erase(view.fullLine(sel))

def insertOrReplace(view, region, string):
	if region:
		view.replace(region, string)
	else:
		view.insert(region.begin(), string)

def handleTabs(view, string):
	if not view.options().get('translateTabsToSpaces'):
		string = string.replace(getTab(view), '\t')

	return string

################################ PLUGIN COMMANDS ###############################

def move_cursor_down(view, cursor_pt, cursor_abs):
	view.sel().clear()

	next_line_starts = view.fullLine(sublime.Region(cursor_abs, cursor_abs)).end()
	next_line = view.line(sublime.Region(next_line_starts, next_line_starts))

	next_line_str = view.substr(next_line).replace('\t', getTab(view))
	tabSize = view.options().get('tabSize', 4)

	if len(next_line_str) < cursor_pt:
		spaces = cursor_pt - len(next_line_str)
		tabs = (spaces / tabSize )
		extra_spaces = (spaces % tabSize) * ' '
		padding = (tabs * tabSize) * ' '
	else:
		extra_spaces = ''
		padding = ''

	next_line_str = handleTabs(view, next_line_str + padding)
	cursor_pt -= ((tabSize -1) * next_line_str.count('\t'))

	if padding: view.replace(next_line, next_line_str + extra_spaces)

	new_pt = next_line.begin() + cursor_pt
	view.sel().add(sublime.Region( new_pt, new_pt ))

def cursor_pos(view):
	"visual `spacing` index  not char index; translates tabs to N spaces"
	
	sel = view.sel()[-1]
	line = view.line(sel)
	
	# character index
	cursor = sel.end()
	chars = view.substr(sublime.Region(line.begin(), sel.end()))

	return len(chars.replace('\t', getTab(view)))

class RelativeIndentCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		sels = view.sel()  

		if args[0] == 'paste':
			clip = textwrap.dedent(sublime.getClipboard()).rstrip().split(u'\n')
			n = len(clip)  

			if len(sels) > 1:   # Columnar Paste
				for region in view.sel():
					insertOrReplace(view, region, clip.pop(0))
			else:
				for i, l in enumerate(clip):
					last_line = i+1 == n	

					sel =  view.sel()[0]			   
					line = view.line(sel)
					if not last_line and view.substr(line).isspace():
						view.runCommand('insertAndDecodeCharacters', ['\n'])	

					cursor_at= cursor_pos(view)
					insertOrReplace(view, sel, l)

					if not last_line:
						move_cursor_down(view, cursor_at, sel.end())
		else:
			for sel in view.sel(): view.sel().add(view.line(sel))
			view.runCommand(args[0])

class ParamPerSelectionSnippetCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		selections = []
		selSet = view.sel()	
		sel1 = selSet[0]

		for sel in selSet:
			selections.append(substrStripPrecedingCommonSpace(view, sel))

		start, end, displace = linesGetFirstsDisplacement( view, sel1) 

		eraseSelectionLines(view)			   
		selSet.clear()

		view.insert(start, (displace * ' ') + '\n')
		putCursorAt = start+displace

		selSet.add(sublime.Region(putCursorAt, putCursorAt))

		view.runCommand('insertSnippet', args + selections)

class RelativeIndentSnippetCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		selSet = view.sel()
		for sel in selSet:
			if sel.empty(): continue

			selectionStripped = substrStripPrecedingCommonSpace(view, sel)
			modifiedRegion = linesFirstNoPrecedingSpace(view, sel)

			selSet.subtract(sel)
			selSet.add(modifiedRegion)
			view.replace(modifiedRegion, selectionStripped) 
			
		view.runCommand('insertSnippet', args)

################################################################################