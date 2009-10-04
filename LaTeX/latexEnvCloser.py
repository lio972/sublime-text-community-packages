import sublime, sublimeplugin

# Insert environment closer
# this only looks at the LAST \begin{...}
# need to extend to allow for nested \begin's

class LatexEnvCloserCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		pattern = r'\\(begin|end)\{[^\}]+\}'
		b = []
		currpoint = view.sel()[0].b
		point = 0
		r = view.find(pattern, point)
		while r and r.end() <= currpoint:
			be = view.substr(r)
			point = r.end()
			if "\\begin" == be[0:6]:
				b.append(be[6:])
			else:
				if be[4:] == b[-1]:
					b.pop()
				else:
					sublime.errorMessage("\\begin%s closed with %s on line %d"
					% (b[-1], be, view.rowcol(point)[0])) 
					return
			r = view.find(pattern, point)
		# now either b = [] or b[-1] is unmatched
		if b == []:
			sublime.errorMessage("Every environment is closed")
		else:
			# note the double escaping of \end
			view.runCommand("insertCharacters \"\\\\end" + b[-1] + "\\n\"")
