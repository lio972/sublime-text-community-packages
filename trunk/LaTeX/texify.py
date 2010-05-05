import sublime, sublimeplugin, os, os.path, re
from subprocess import Popen, PIPE, STDOUT

# Compile TEX file in current buffer using MikTeX's "texify" command
# Does not start the previewer
# If the buffer has been modified, it saves it
# Also create SyncTeX file (for inverse/forward search);
# the viewPDF command implements inverse search (i.e. tells SumatraPDF to call
# back Sublime Text when the user double-clicks on the page)
# Only a minimal sanity check is implemented.

DEBUG = 0
quotes = "\""

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
		# --max-print-line makes sure that no line is truncated, or we would not catch
		# line numbers in some warnings
		texify = u'texify -b -p --tex-option=\"--synctex=1\" --tex-option=\"--max-print-line=200\" '
		cmd = texify + quotes + texFile + texExt + quotes
		print "\n\nTexify executing command:"
		print cmd
		p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
		(stdoutdata, stderrdata) = p.communicate()
		if stderrdata and not("see log file" in str(stderrdata)):
			sublime.errorMessage("Could not invoke texify. Got the following error:\n%s" % (str(stderrdata),) )
			print "texify invocation error:" + str(stderrdata)
			print len(stdoutdata),len(stderrdata)
		else:	
			window.runCommand('showTeXError')

class ShowTeXErrorCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		print "Show tex errors"
		errors = []
		warnings = []
		texFile = os.path.splitext(window.activeView().fileName())[0]
		try:
			# Read it in as binary, as there may be NULLs
			# No need to close as we do not create a file object
			logdata = open(texFile + ".log", 'rb').read()
		except IOError:
			sublime.errorMessage("Cannot open log file %s!" % (texFile + ".log",))
			return
		log = logdata.splitlines()
		errors = [line for line in log if line[0:2] in ['! ','l.']]
		warnings = [line for line in log if "LaTeX Warning: " in line]
		panelContent = []
		if errors:
			print "There were errors.\n"
			skip = 0
			for error in errors:
				print error[:-1]
				if skip:
					print ""
				skip = 1-skip
			panelContent.append("There were errors in your LaTeX source") 
			panelContent.append("Click on any message below that shows a line number")
			panelContent.append("")
			panelContent.extend(errors)
		else:
			print "No errors.\n"
			panelContent.append("Texification succeeded: no errors!\n")
			panelContent.append("") 
		if warnings:
			print "There were no warnings.\n"
			skip = 0
			for warning in warnings:
				print warning[15:]
				if skip:
					print ""
				skip = 1-skip
			if errors:
				panelContent.append("")
				panelContent.append("There were also warnings.") 
				panelContent.append("You can click on these, too.")
			else:
				panelContent.append("However, there were warnings in your LaTeX source") 
				panelContent.append("Click on any message below that shows a line number")
			panelContent.append("")
			panelContent.extend(warnings)
		else:
			print "No warnings.\n"
		
		window.showQuickPanel("", "gotoTeXError", panelContent, panelContent, sublime.QUICK_PANEL_MONOSPACE_FONT)



		
class GotoTeXErrorCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		message = args[0]
#		print error
		if "LaTeX Warning:" in message:
			p = re.compile('input line (\d*)')
		else:
			p = re.compile('[^\d]*(\d*)')
		lineno = p.search(message).group(1)
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