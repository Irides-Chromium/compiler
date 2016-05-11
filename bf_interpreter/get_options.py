#!/usr/bin/python3

from getopt import getopt, GetoptError
import sys

def read_opts():
    cell_size = 1           # count of bytes
    tape_size = 30000       # count of cells
    wrap_cell = True        # no notify on overflow or downflow
    wrap_tape = False       # when RP > tape_size, back to 0 and continue
    temp_regs = False       # has a temporary register
    doub_tape = False       # use two tapes instead of one
    rept_macr = False       # use numbers to repeat
    hard_set = False        # allow user to change source file default opts

    try:
        opts, args = getopt(sys.argv[1:], "h:r:d:t:o:", 
                ["cell-size=", "tape-size=", "wrap-cell=", "wrap-tape=", 
                "temp-regs", "double-tape", "rept-macro", "hard", "help"])
    except GetoptError:
        print_help()
        sys.exit(2)
    print(opts)
    print(args)
    for opt, arg in opts:
        print(opt, arg)
        if opt in ('-h', '--help'):
            print_help()
            sys.exit()
        elif opt in ('-r', '--rept-macro'):
            rept_macr = True
        elif opt in ('-d', '--double-tape'):
            doub_tape = True
        elif opt in ('-t', '--temp-regs'):
            temp_regs = True
        elif opt == '--cell-size':
            cell_size = int(arg)
        elif opt == '--tape-size':
            tape_size = int(arg)
        elif opt == '--wrap-cell':
            wrap_cell = True
        elif opt == '--wrap-tape':
            wrap_tape = True
        elif opt == '--hard':
            hard_set = True

    return cell_size, tape_size, wrap_cell, wrap_tape, \
        temp_regs, doub_tape, rept_macr, hard_set

def print_help():
    pass

print(read_opts())
