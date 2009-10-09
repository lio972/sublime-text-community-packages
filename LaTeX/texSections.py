import sublime, sublimeplugin, os, os.path, re

# References and citations

spaces = {'part' : '', 'chapter' : '  ', 'section' : '    ',
		  'subsection' : '      ', 'subsubsection' : '        ',
		  'subsubsubsection' : '          '}

class TexSectionsCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		# First get raw \section{xxx} lines
		# Note that these may be followed by \label{xxx}
		sections = []
		view.findAll(r'\\(part|chapter|(?:sub)*section)\{(.+)\}',0,r"\\\1\{\2\}",sections)
		# Now filter out possible ending \label{xxx}'s
		def killLabel(s):
			#print "kill " + s
			# Assume first { has been skipped: e.g. "Title of section}"
			# Will return text except for final }
			n = 1
			news = ""
			for c in s:
				#print c,n
				if c == '}':
					n -= 1
					if n == 0:
						#print news
						return news
				elif c == '{':
					n += 1
				news += c
				#print news
		#print killLabel("hel\label{test}p} \label{test2}")
		#print sections
		# len(key)+2 to skip initial \ and first {
		fsections = [spaces[key] + killLabel(sec[len(key)+2:])
					 for sec in sections 
					 # 1:1+len(key) to skip initial \
					 for key in spaces.keys() if sec[1:1+len(key)] == key]

		#print fsections
		def onSelect(i):
			seci = sections[i]
			#print seci
			#note flag sublime.LITERAL, so "{", "(", "\" are all OK
			linept = view.find(seci,0,sublime.LITERAL).end()
			s = view.sel() # RegionSet
			s.clear()
			s.add(sublime.Region(linept,linept))
			view.show(linept)
			view.runCommand("moveTo bol")

		view.window().showSelectPanel(fsections, onSelect, None, 0)
		#print "done2"

