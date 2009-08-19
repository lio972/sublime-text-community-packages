import sublime, sublimeplugin

import subprocess
import os

# This plugin provides access to frequently used Mercurial commands
#
# To use this plugin, Mercurial must be in your path.
# To verify this, open a command prompt and type 'hg'
# If you get a list of commands, it's on the path, otherwise, add it to the path
#
# You may obtain Mercurial at: http://mercurial.selenic.com/wiki/

class MercurialCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		# don't operate unless the buffer is saved
		if(view.fileName() == None):
			return

		# Put the file name in quotes to allow spaces in the name			
		bufferName = "\"" + str(view.fileName()) + "\""
		
		# Parse the arguments
		if(args[0]=="commit"):
			Results = doSystemCommand("hg commit")
			displayResults(Results, "MessageBox", None)
		elif(args[0]=="addCurrent"):
			Results = doSystemCommand("hg add " + bufferName)
			displayResults(Results, "MessageBox", None)
		elif(args[0]=="initCurrent"):
			Results = doSystemCommand("hg init")
			displayResults(Results, "MessageBox", None)
		elif(args[0]=="removeCurrent"):
			Results = doSystemCommand("hg remove " + bufferName)
			displayResults(Results, "MessageBox", None)
		elif(args[0]=="diff"):
			Results = doSystemCommand("hg diff " + bufferName)
			displayResults(Results, "Window", view)
		elif(args[0]=="push"):
			Results = doSystemCommand("hg push ")
			displayResults(Results, "MessageBox", None)
		elif(args[0]=="pull"):
			Results = doSystemCommand("hg pull")
			displayResults(Results, "MessageBox", None)
		elif(args[0]=="update"):
			Results = doSystemCommand("hg update")
			displayResults(Results, "MessageBox", None)
		elif(args[0]=="pullAndUpdate"):
			Results = doSystemCommand("hg pull -u ")
			displayResults(Results, "Window", view)
		elif(args[0]=="revert"):
			Results = doSystemCommand("hg revert " + str(bufferName))
			displayResults(Results, "Window", view)
		elif(args[0]=="status"):
			Results = doSystemCommand("hg status")
			displayResults(Results, "Window", view)

# Runs a system command from the command line
# Captures and returns both stdout and stderr as an array, in that respective order
def doSystemCommand(commandText):
	p = subprocess.Popen(commandText, shell=True, bufsize=1024, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	stdout = p.stdout
	stderr = p.stderr
	return [stdout.read(),stderr.read()]
	
# Displays given stderr if its not blank, otherwise displays stdout
# Method of display is configured using the Mode argument
#
# Results is of the form
# Results[0] is stdout to display
# Results[1] is stderr which, if its not None, will be displayed instead of stdout
#
# Modes:
# 	Window - Opens a new buffer with output
#	MessageBox - Creates a messageBox with output
#
# view is the view that will be used to create new buffers

def displayResults(Results, Mode, view):
	if(Mode == "Window"):
		if(Results[1] != None and Results[1] != ""):
			createWindowWithText(view, "An error or warning occurred:\n\n" + str(Results[1]))
		elif(Results[0] != None and Results[0] != ""):
			createWindowWithText(view, str(Results[0]))			
	# Message Box
	elif(Mode == "MessageBox"):
		if(Results[1] != None and Results != ""):
			sublime.messageBox("An error or warning occurred:\n\n" + str(Results[1]))
		elif(Results[0] != None and Results[0] != ""):
			sublime.statusMessage(str(Results[0]))

# Open a new buffer containing the given text			
def createWindowWithText(view, textToDisplay):
	MercurialView = sublime.Window.newFile(view.window())
	MercurialView.insert(MercurialView.size(), textToDisplay)