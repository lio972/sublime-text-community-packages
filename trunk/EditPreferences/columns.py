#################################### IMPORTS ###################################

import os
import math

################################### SETTINGS ###################################

SCREEN_WIDTH = 150      # char width of quick panel (select then copy => status)

CELL_ALIGN = unicode.ljust                           # rjust for right alignment 
                            
STRIP = unicode.rstrip                                    # see ellpsis function

POWARRAH = -0.5 

CELL_PADDING = 2

DECODE = lambda s: s.decode('utf8', 'ignore')

############################### COLUMN RENDERING ###############################

def find_widths(columns, total_width=SCREEN_WIDTH, cell_padding=CELL_PADDING):
    O = int(len(columns[0]) / 10.0)

    # Find the average, discarding some outliers
    seq =  [ (sum(len(element) for element in L) /len(L)) for L in   
             [sorted(S)[O:len(S)-O] for S in columns] ]

    n = len(columns)
    screen_width = total_width - n * cell_padding  # padded by render_rows func

    # power scaling; smaller columns get bigger share of leftovers
    seq = [x * (float((x ** POWARRAH) * screen_width)/sum(seq)) for x in seq]

    # Distribute the leftovers
    column_widths = [ int( x*screen_width/sum(seq) )  for x in seq]

    for i, col in enumerate(columns):
        # Pop off a column width
        colw = column_widths.pop(0)
        maxw = max(len(l) for l in col)
        width = min(maxw, colw)

        # If there is leftovers (column assigned more width than its largest
        # cell) then redistribute the wealth amongst the remaining columns
        # As cell padding has already been accounted set cell padding to 0
        # for recursive call

        if maxw < colw:
            remaining_cols = columns[i+1:]
            remaining_width = abs( maxw - colw ) + sum(column_widths)
            if remaining_cols:
                column_widths = list ( 
                    find_widths(remaining_cols, remaining_width, 0) )

        yield width

def pad_columns(columns, align=CELL_ALIGN):
    padded = []
    
    for i, (col, width) in enumerate(zip(columns, find_widths(columns))):
        def ellipsis(s):
            # If it is the last column just let it overhang, no sense in cutting
            return ( s if (len(s) <= width or i+1 == len(columns)) 
                     else s[:width-3] + ' ..')

        # rstrip each cell
        padded.append([align(ellipsis(STRIP(DECODE(c))), width) for c in col ])
    return padded

# Assumes all columns and rows or of equal length

def columns_2_rows(columns): # [[], [], []]
    return [tuple(a[i] for a in columns) for i in xrange(len(columns[0]))]

def rows_2_columns(rows):
    [ [r[i] for r in rows] for i,_ in enumerate(rows[0])]

def rendered_rows(rows, pl=0, pr=CELL_PADDING):
    # render each row as unicode with padded cells to stop them getting lonely
    pad = lambda r: [(pl*' ') + c + (pr*' ') for c in r]
    return [''.join(pad(r)) for r in rows]

def remove_common_prefix(col):
    common_prefix = os.path.commonprefix(col)
    return [cell[len(common_prefix):] for cell in col]

def format_for_display(args, cols=(), paths=()):
    columns = [ [a[i] for a in args] for i in cols or range(len(args[0])) ]
    # Remove common prefixes (super long columns)
    columns = [ remove_common_prefix(c) if i in paths else c
                for i, c in enumerate(columns) ]
    return rendered_rows(columns_2_rows(pad_columns(columns)))

################################################################################