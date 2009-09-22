import sublime, sublimeplugin, os, os.path
from subprocess import Popen

# View PDF file corresonding to TEX file in current buffer
# Assumes that the SumatraPDF viewer is used (great for inverse search!)
# and its executable is on the %PATH%
# Warning: we do not do "deep" safety checks (e.g. see if PDF file is old)

class ViewPDFCommand(sublimeplugin.WindowCommand):
	def run(self, window, args):
		view = window.activeView()
		texFile, texExt = os.path.splitext(view.fileName())
		if texExt.upper() != ".TEX":
			sublime.errorMessage("%s is not a TeX source file: cannot view." % (os.path.basename(view.fileName()),))
			return
		quotes = "\""
		pdfFile = quotes + texFile + u'.pdf' + quotes
		sumatra = u'SumatraPDF -reuse-instance -inverse-search \"sublimetext \\\"%f\\\":%l\" '
		print sumatra + pdfFile
		Popen(sumatra + pdfFile)
