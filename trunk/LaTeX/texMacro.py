import sublime, sublimeplugin

macros = { 
'a' : '\\alpha',
'b' : '\\beta',
'c' : '\\chi',
'd' : '\\delta',
'e' : '\\epsilon',
'f' : '\\phi',
'g' : '\\gamma',
'h' : '\\eta',
'i' : '\\iota',
'j' : '\\phi',
'k' : '\\kappa',
'l' : '\\lambda',
'm' : '\\mu',
'n' : '\\nu',
'o' : '\\omicron',
'p' : '\\pi',
'q' : '\\theta',
'r' : '\\rho',
's' : '\\sigma',
't' : '\\tau',
'u' : '\\upsilon',
'v' : '\\psi',
'w' : '\\omega',
'x' : '\\xi',
'y' : '\\vartheta',
'z' : '\\zeta',
'>=' : '\\geq',
'<=' : '\\leq',
'->' : '\\rightarrow',
'=>' : '\\Rightarrow',
'<=>' : '\\Leftrightarrow',
'>' : '\\rangle',
'<' : '\\langle',
'lp' : '\\left(',
'rp' : '\\right)',
'A' : '\\forall',
'B' : 'FREE',
'C' : '\\Chi',
'D' : '\\Delta',
'E' : '\\exists',
'F' : '\\Phi',
'G' : '\\Gamma',
'H' : 'FREE',
'I' : '\\bigcap',
'J' : '\\Phi',
'K' : 'FREE',
'L' : '\\Lambda',
'M' : '\\int',
'N' : '\\sum',
'O' : '\\emptyset',
'P' : '\\Pi',
'Q' : '\\Theta',
'R' : 'FREE',
'S' : '\\Sigma',
'T' : '\\times',
'U' : '\\bigcup',
'V' : '\\Psi',
'W' : '\\Omega',
'X' : '\\Xi',
'Y' : '\\Upsilon',
'Z' : '\\sum' 
}

class texMacroCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		k = args[0]
		print "texMacro: " + k
		if k:
			# the following incantation means: 
			# 1. take the selection; this is a RegionSet
			# 2. get the first region (arbitrary, because this command is not meant
			#    to be used with selections anyway)
			# 3. take the endpoint and insert
			view.insert(view.sel()[0].b, macros[k])
