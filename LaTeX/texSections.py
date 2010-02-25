import sublime, sublimeplugin, os, os.path, re

# References and citations

spaces = {'part' : '', 'chapter' : '  ', 'section' : '    ',
		  'subsection' : '      ', 'subsubsection' : '        ',
		  'subsubsubsection' : '          '}

class TexSectionsCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		# First get raw \section{xxx} lines
		# Capture the entire line beginning with our pattern, do processing later
		secRegions = view.findAll(r'^\\(begin\{frame\}|part|chapter|(?:sub)*section).*$')
		# Remove \section, etc and only leave spaces and titles
		# Handle frames separately
		# For sections, match \ followed by type followed by * or {, then
		# match everything. This captures the last }, which we'll remove
		secRe = re.compile(r'\\([^{*]+)\*?\{(.*)') # \, then anything up to a * or a {
		# Also, we need to remove \label{} statements
		labelRe = re.compile(r'\\label\{.*\}')
		# And also remove comments at the end of the line
		commentRe = re.compile(r'%.*$')
		# This is to match frames
		# Here we match the \begin{frame} command, with the optional [...]
		# and capture the rest of the line for further processing
		# TODO: find a way to capture \frametitle's on a different line
		frameRe = re.compile(r'\\begin\{frame\}(?:\[[^\]]\])?(.*$)')
		frameTitleRe = re.compile(r'\{(.*)\}')
		def prettify(s):
			s = commentRe.sub('',s).strip() # kill comments at the end of the line, blanks
			s = labelRe.sub('',s).strip() # kill label statements
			frameMatch = frameRe.match(s)
			if frameMatch:
				frame = frameMatch.group(1)
				frameTitleMatch = frameTitleRe.search(frame)
				if frameTitleMatch:
					return "frame: " + frameTitleMatch.group(1)
				else:
					return "frame: (untitled)"
			else:
				m = secRe.match(s)
				#print m.group(1,2)
				secTitle = m.group(2)
				if secTitle[-1]=='}':
					secTitle = secTitle[:-1]
				return spaces[m.group(1)]+secTitle
		prettySecs = [prettify(view.substr(reg)) for reg in secRegions]
		
		def onSelect(i):
			#print view.substr(secRegions[i])
			view.show(secRegions[i])
			s = view.sel() # RegionSet
			s.clear()
			s.add(secRegions[i])
			view.runCommand("moveTo bol")

		view.window().showSelectPanel(prettySecs, onSelect, None, 0)
