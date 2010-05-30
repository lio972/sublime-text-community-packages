import sublime, sublimeplugin, os, os.path, re
from subprocess import Popen, PIPE, STDOUT
import threading, functools, ctypes

# Compile TEX file in current buffer using MikTeX's "texify" command
# Does not start the previewer
# If the buffer has been modified, it saves it
# Also create SyncTeX file (for inverse/forward search);
# the viewPDF command implements inverse search (i.e. tells SumatraPDF to call
# back Sublime Text when the user double-clicks on the page)
# Only a minimal sanity check is implemented.

DEBUG = 0
quotes = "\""

# From guillermoo's PowerShell utils

def getOEMCP():
    # Windows OEM/Ansi codepage mismatch issue.
    # We need the OEM cp, because texify and friends are console programs
    codepage = ctypes.windll.kernel32.GetOEMCP()
    return str(codepage)



# Actually parse tex log
# Input: tex log file (decoded), split into lines
# Output: content to be displayed in quick panel, split into lines
# 
# We do very simple matching:
#    "!" denotes an error, so we catch it
#    "Warning:" catches LaTeX warnings, as well as missing citations, and more

def parseTeXlog(log):
	print "Parsing log file"
	errors = []
	warnings = []
	errors = [line for line in log if line[0:2] in ['! ','l.']]
	warnings = [line for line in log if "Warning: " in line]
	panelContent = []
	if errors:
		print "There were errors.\n"
		skip = 0
		for error in errors:
			print error[:-1]
			# skip a line?
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
			print warning
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
	return panelContent



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

		pContents = ["Texify executing command:", cmd]
		window.showQuickPanel("texify", "", pContents)

		# Execute command in a thread
		# First, define class 

		class CmdThread ( threading.Thread ):

			# Use __init__ to pass things we need, including window
			# so we can get window.showQuickPanel
			def __init__ (self, cmd, pContent, texFile, window):
				self.cmd = cmd
				self.pContent = pContent
				self.texFile = texFile
				self.qp = window.showQuickPanel
				threading.Thread.__init__ ( self )

			def run ( self ):
				print "Welcome to the thread!"
				#print self.cmd
				#print self.pContent
				p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
				stdoutdata, stderrdata = p.communicate()
				# display errors and warnings from last generated log file,
				# followed by the full output of the texify command
				# (if we only use the texify output, we get multiple errors/warnings, and also
				# warnings about e.g. references that are corrected in subsequent runs)
				texifyLog = stdoutdata.decode(getOEMCP()).splitlines()
				try:
					# Read it in as binary, as there may be NULLs
					# No need to close as we do not create a file object
					log = open(texFile + ".log", 'rb').read().decode(getOEMCP()).splitlines()
				except IOError:
					# if we cannot read the log file for any reason,
					# just use the texify output
					log = texifyLog
				pContent = self.pContent + ["",] + parseTeXlog(log) + \
							["","********************", "", "Full texify output follows", \
							"Remember: texify may run latex & friends many times; missing refs. etc. may get automatically fixed in later runs",\
							"", "********************", "", ""] + texifyLog
				sublime.setTimeout(functools.partial(self.qp,"texify","gotoTeXError", pContent), 0)
				print "returned from qp in thread"

				# if stderrdata and not("see log file" in str(stderrdata)):
				# 	sublime.errorMessage("Could not invoke texify. Got the following error:\n%s" % (str(stderrdata),) )
				# 	print "texify invocation error:" + str(stderrdata)
				# 	print len(stdoutdata),len(stderrdata)
				# else:	
				# 	window.runCommand('showTeXError')
		
		CmdThread(cmd, pContents, texFile, window).start()





class ShowTeXErrorCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		print "Show tex errors"
		pname = "texify" if args else "" # just as extra precaution
		print "Panel name: " + pname
		texFile = os.path.splitext(window.activeView().fileName())[0]
		try:
			# Read it in as binary, as there may be NULLs
			# No need to close as we do not create a file object
			log = open(texFile + ".log", 'rb').read().decode(getOEMCP()).splitlines()
		except IOError:
			sublime.errorMessage("Cannot open log file %s!" % (texFile + ".log",))
			return
		panelContent = parseTeXlog(log) + \
							["","********************", "", "Last generated log file follows", \
							"", "********************","",""] + log
		window.showQuickPanel(pname, "gotoTeXError", panelContent, panelContent, sublime.QUICK_PANEL_MONOSPACE_FONT)



		
class GotoTeXErrorCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		message = args[0]
#		print error
		# this catches both references and citations (and perhaps more!)
		if "Warning:" in message:
			p = re.compile('input line (\d+)')
		else:
			p = re.compile('[^\d]*(\d+)')
		linenoSearchResult = p.search(message)
		print linenoSearchResult
		if linenoSearchResult:
			lineno = linenoSearchResult.group(1)
		else:
			return
		v = window.activeView()
		linept = v.textPoint(int(lineno)-1,0) # lineno is 1-based here
		s = v.sel() # RegionSet
		s.clear()
		s.add(sublime.Region(linept,linept))
		v.show(linept)