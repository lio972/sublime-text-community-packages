import sublime, sublimeplugin, os.path

# Jump to current line in PDF file

class JumpToPDFCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		texFile, texExt = os.path.splitext(view.fileName())
		if texExt.upper() != ".TEX":
			sublime.errorMessage("%s is not a TeX source file: cannot jump." % (os.path.basename(view.fileName()),))
			return
		quotes = "\""
		srcfile = texFile + u'.tex'
		pdffile = texFile + u'.pdf'
		(line, col) = view.rowcol(view.sel()[0].end())
		print "Jump to: ", line,col
		# column is actually ignored up to 0.94
		# HACK? It seems we get better results incrementing line
		line += 1
		# the last params are flags. In part. the last is 0 if no focus, 1 to focus
		command = "[ForwardSearch(\"%s\",\"%s\",%d,%d,0,0)]" % (pdffile, srcfile, line, col)
		view.runCommand("sendDDEExecute",["SUMATRA","control",command])