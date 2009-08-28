import sublime, sublimeplugin

import subprocess, os.path

class PerlTidyCommand(sublimeplugin.TextCommand):
	"""
	Use this command to pretty print Perl code.

	It pretty-prints the selected region or the entire file.

	Will use the installed PerlTidy if found, else will use the embedded
	PerlTidy in which case a Perl interpreter must be in the PATH environment variable

	See http://perltidy.sourceforge.net/ for more information
	"""

	# Default path to PerlTidy, change this to your own PerlTidy installation if you have one
	DefaultPerlTidy = 'C:/Perl/site/bin/perltidy'
	
	# Pretty printing parameters, customize to your liking
	PrettyPrintingParams = [
		"-sbl",   # open sub braces on new line
		"-bbt=1", # add only some spaces in single-line curly braces
		"-pt=2",  # dont add spaces inside parenthesis
		"-nbbc",  # don't add blank lines before comments
		"-l=100", # wrap at column 100
	]

	def run(self, view, args):
		if(view.sel()[0].empty()):
			# nothing selected: process the entire file
			self.tidyRegion(view, sublime.Region(0L, view.size()))
		else:
			# process only selected region
			self.tidyRegion(view, view.line(view.sel()[0]))

	def tidyRegion(self, view, region):
		if(os.path.isfile(self.DefaultPerlTidy)):
			# use installed PerlTidy
			cmd = [self.DefaultPerlTidy]
			# print "using installed PerlTidy", cmd
		else:
			# use packaged PerlTidy, needs Perl to run
			cmd = ["perl", sublime.packagesPath() + "/PerlTidy/perltidy"]
			# print "using packaged PerlTidy", cmd

		cmd += [
			"-w", # report all errors and warnings
			"-se" # send error message to stderr rather than filename.err
		]

		cmd += self.PrettyPrintingParams # add pretty printing parameters

		p = subprocess.Popen(
			cmd,
			shell   = True,
			bufsize = -1,
			stdout  = subprocess.PIPE,
			stderr  = subprocess.PIPE,
			stdin   = subprocess.PIPE)

		output, error = p.communicate(view.substr(region))

		view.replace(region, output)

		if error:
			print "\nPerlTidy error:\n", error
			sublime.statusMessage("Error detected, check output panel for more information")

	def isEnabled(self, view, args):
		# enabled for Perl files, with at most 1 selection region
		return len(view.sel()) == 1 and view.options().getString("syntax") == "Packages/Perl/Perl.tmLanguage"