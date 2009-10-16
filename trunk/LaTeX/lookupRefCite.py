import sublime, sublimeplugin, re, textwrap

# Lookup label (cross-reference) or bibliography entry (citation)
# Position cursor right after closing }

# Params:
# How many chars before
AROUND = 200
# Column width for Quick Panel
WIDTH = 80

class LookupRefCiteCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		# We need a slightly more sophisticated def of "current word"
		currsel = view.sel()[0]
		currline = view.line(currsel)
		text = view.substr(sublime.Region(currline.begin(),currsel.end()))
		print text
		# now we search for either \ref, \eqref, etc. or \cite, \citet...
		m = re.search(r'.*\\(.+)\{(.+)\}$', text)
		if m:
			(typ, lab) = m.groups()
			if "ref" in typ:	# it's a reference, show text around it
				cmd = "\\\\label\{%s\}" % (lab,)
				print cmd
				r = view.find(cmd,0)
				around = sublime.Region(max(r.begin()-AROUND,0), min(r.end()+AROUND,view.size()))
				textaround = ("..."+view.substr(around)+"...").split('\n')
				textjust = []
				for line in textaround:
					textjust.extend(textwrap.wrap(line, WIDTH))
				view.window().showQuickPanel("", "move words 0", textjust) # dummy command
			elif "cite" in typ: # it's some kind of citation, get it from BibTeX
				pass # to be implemented
