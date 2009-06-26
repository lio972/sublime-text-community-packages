#################################### IMPORTS ###################################

import os
import math
import random

################################### SETTINGS ###################################

SCREEN_WIDTH = 150      # char width of quick panel (select then copy => status)

CELL_ALIGN = unicode.ljust                           # rjust for right alignment

STRIP = unicode.rstrip                                    # see ellpsis function

POWARRAH = -0.5

CELL_PADDING = 2

DECODE = lambda s: s.decode('utf8', 'ignore')

############################### COLUMN RENDERING ###############################

def normed_column_widths(columns):
    outliers = int(columns and len(columns[0] or 0) / 10.0)

    # Find the average, discarding some outliers
    return  [ (sum(len(e) for e in col) / (len(col) or 1)) for col in
             [sorted(col)[outliers:len(col)-outliers] for col in columns] ]

def yield_widths(columns, total_width=SCREEN_WIDTH, cell_padding=CELL_PADDING):
    colw = normed_column_widths(columns)

    n = len(columns)
    screen_width = total_width - n * cell_padding  # padded by render_rows func

    # power scaling; smaller columns get bigger share of leftovers
    scaling = [ x * (float( ( x ** POWARRAH ) * screen_width)/sum(colw))
                if x else 0
                for x in colw ]

    # Distribute the leftovers
    column_widths = [ int( s * screen_width/sum(scaling) ) for s in scaling]

    for i, col in enumerate(columns):
        # Pop off a column width
        colw = column_widths.pop(0)
        maxw = max(len(l) for l in col)

        width = min(maxw, colw)

        if maxw < colw:
            remaining_cols = columns[i+1:]
            remaining_width = abs( maxw - colw ) + sum(column_widths)
            if remaining_cols:
                column_widths = list (
                    yield_widths(remaining_cols, remaining_width, 0) )

        yield width

def find_widths(columns):
    lengths = normed_column_widths(columns)
    tosort = sorted ((
        (i, lengths[i]) for i in xrange(len(columns)) ), key=lambda t: t[1] )

    widths = list(yield_widths([columns[i] for i in [s[0] for s in tosort] ]))

    for i, w in enumerate(widths):
        lengths[ tosort[i][0] ] = w

    return lengths

def pad_columns(columns, align=CELL_ALIGN):
    padded = []

    for i, (col, width) in enumerate(zip(columns, find_widths(columns))):
        def ellipsis(s):
            # If it is the last column just let it overhang, no sense in cutting
            return ( s if (len(s) <= width
                        or i+1 == len(columns)
                    )
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
    return [''.join(pad(r)).decode('utf8', 'ignore') for r in rows]

def remove_common_prefix(col):
    common_prefix = os.path.commonprefix(col)
    return [cell[len(common_prefix):] for cell in col]

def format_for_display(args, cols=(), paths=()):
    columns = [ [a[i] for a in args] for i in cols or range(len(args[0])) ]
    # Remove common prefixes (super long columns)
    columns = [ remove_common_prefix(c) if i in paths else c
                for i, c in enumerate(columns) ]
    return rendered_rows(columns_2_rows(pad_columns(columns)))

############################### FUCKAROUND TESTS ###############################

def test():
    cols = (40, 80)
    col2 = (5,  10)
    col3 = (5,  10)
    col4 = (5,  10)

    args = []

    for i in range(100):
        args.append ((
            random.randint(*cols) * 'a',
            random.randint(*col2) * 'b',
            random.randint(*col3) * 'c',
            random.randint(*col4) * 'c',
        ))

    args = format_for_display(args)
    print '\n'.join(args)
    print max(len(l.rstrip()) for l in args)

if __name__ == '__main__':
    test()

################################################################################