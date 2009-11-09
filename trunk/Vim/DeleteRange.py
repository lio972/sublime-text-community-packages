import sublime, sublimeplugin
import re

def abs(n):
	if n < 0: return -1 * n
	else: return n
	
# and type: view.runCommand('deleteRange')
class DeleteRangeCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		for command in " ".join(args).split(","):
			self.parse(view, command)
	
	##------------------------------------------------------------------------------
	def parse(self, view, command):
		match_line_pattern = "lines ([-]?\d+)"
		if re.match(match_line_pattern, command):
			self.line(view, int(re.match(match_line_pattern, command).group(1)))

		match_word_pattern = "words ([-]?\d+)"
		if re.match(match_word_pattern, command):
			self.word(view, int(re.match(match_word_pattern, command).group(1)))

		match_character_pattern = "characters ([-]?\d+)"
		if re.match(match_character_pattern, command):
			self.character(view, int(re.match(match_character_pattern, command).group(1)))

		match_eol_pattern = "eol"
		if re.match(match_eol_pattern, command):
			self.eol(view)

		match_bol_pattern = "bol"
		if re.match(match_bol_pattern, command):
			self.bol(view)			
			
	##------------------------------------------------------------------------------
	def line(self, view, n):
		if n < 0:
			view.runCommand('move lines ' + str(n))
		for i in range(abs(n)):
			view.runCommand('expandSelectionTo line')
			view.runCommand('leftDeleteCharacters')		

	##------------------------------------------------------------------------------
	def word(self, view, n):
		if n < 0: 
			direction = "left"
		else: 
			direction = "right"
		
		for i in range(abs(n)):
			view.runCommand('deleteWord ' + direction)	

	##------------------------------------------------------------------------------
	def character(self, view, n):
		if n < 0: 
			direction = "left"
		else: 
			direction = "right"
		
		for i in range(abs(n)):
			view.runCommand(direction + 'DeleteCharacters')

	##------------------------------------------------------------------------------
	def eol(self, view):
		view.runCommand('moveTo eol extend')
		view.runCommand('rightDeleteCharacters')

	##------------------------------------------------------------------------------
	def bol(self, view):
		view.runCommand('moveTo bol extend')
		view.runCommand('leftDeleteCharacters')