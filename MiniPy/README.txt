MiniPy plugin

evaluate the selected text as python script, pasted back instead of the selected text

example 1. mark the column with the 'x+1' on the code below, and press ctrl+e
	arr[x+1] -> arr[1]
	arr[x+1] -> arr[2]
	arr[x+1] -> arr[3]
	arr[x+1] -> arr[4]

example 2. 
	random()           -> 0.215884125091
	x				   -> 0.215884125091
	sin(1.2)           -> 0.932039085967
	1+2+3              -> 6
	34*5.5             -> 187.0
	"x" * 10           -> xxxxxxxxxx
	len("abracadabra") -> 11
	x				   -> 11 				# the result of previous len is assigned to x
	x*2 			   -> 22 				# the result of previous line is multiplied by 2
