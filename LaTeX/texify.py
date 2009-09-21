import sublime, sublimeplugin, os, os.path, re
from subprocess import Popen, PIPE, STDOUT

# Compile TEX file in current buffer using MikTeX's "texify" command
# Does not start the previewer
# If the buffer has been modified, it saves it
# Also create SyncTeX file (for inverse/forward search);
# the viewPDF command implements inverse search (i.e. tells SumatraPDF to call
# back Sublime Text when the user double-clicks on the page)
# Only a minimal sanity check is implemented.

# For debugging purposes, we capture the output of "texify".
# Whe the command has been shown to work, this is redundant, as the LaTeX-relevant
# information is already in <basename>.log

DEBUG = 0

class TexifyCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		# Save file if necessary
		view = window.activeView()
		texFile, texExt = os.path.splitext(view.fileName())
		if texExt.upper() != ".TEX":
			sublime.errorMessage("%s is not a TeX source file: cannot compile." % (os.path.basename(view.fileName()),))
			return
		if view.isDirty():
			print "saving..."
			window.runCommand('save')
		texify = u'texify -b -p --tex-option=\"--synctex=1\" '
		cmd = texify + texFile + texExt
		if DEBUG:
			output = open(texFile + ".texify", 'w')
			output.write(cmd + "\n")
		print "\n\nTexify executing command:"
		print cmd
		if DEBUG:
			Popen(cmd, stdout=output, stderr=STDOUT)
			output.close()
		else:
			p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=False)
			(stdoutdata, stderrdata) = p.communicate()
		window.runCommand('showTeXError')

class ShowTeXErrorCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		texFile = os.path.splitext(window.activeView().fileName())[0]
		logfile = open(texFile + ".log")
		log = logfile.readlines()
		logfile.close()
		errors = [line for line in log if line[0:2] in ['! ','l.']]
		if errors:
			print "There were errors.\n"
			skip = 0
			for error in errors:
				print error[:-1]
				if skip:
					print ""
				skip = 1-skip
			panelText = ["There were errors in your LaTeX source", 
						 "Click on any message below that shows a line number",
						 ""]
			window.showQuickPanel("", "gotoTeXError", panelText + errors)
		else:
			print "No errors. Goodbye!\n"




		
class GotoTeXErrorCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		error = args[0]
#		print error
		p = re.compile('[^\d]*(\d*)')
		lineno = p.search(error).group(1)
		if lineno == '':
			return
#		print lineno
		# goto line: isn't there a smarter way?
		v = window.activeView()
		linept = v.textPoint(int(lineno)-1,0) # lineno is 1-based here
		s = v.sel() # RegionSet
		s.clear()
		s.add(sublime.Region(linept,linept))
		v.show(linept)