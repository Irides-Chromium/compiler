#!/usr/bin/python3

# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# This is the original brainfuck interpreter with the pbrain extension and
# a temporary register
# Avaliable Operators:
# + - < > [ ] , . ( ) : @ !

import time
import sys
from putchar import putchar

CL_S = 256         # the maximum number allowed + 1
TP_S = 30000       # count of cells
input_stream = ""
RT = [0 for i in range(TP_S)]            # Register tape (paper tape)
RP = 0                                   # Register Pointer
func_tape = [None for i in range(CL_S)]  # Function tape
reg = 0                                  # Temporary register

def run_console():
    print("Brainfuck Interpreter 1.0.2 (W: pbrain not usable)")
    print("Use '#' to inspect tape")
    while True:
        try: execute(input(">>> "))
        except (EOFError, KeyboardInterrupt): sys.exit(print())

def run_file(filename):
    try: execute(open(filename, "r").read())
    except IOError: sys.exit(print("%s: cannot find %s: no such file" % \
                (sys.argv[0], filename)))

def cur_val():
    return RT[RP]

def add(value):
    RT[RP] += value
    RT[RP] %= CL_S

def mov(diff):
    global RP
    RP += diff
    if RP < 0: sys.exit("error: tape memory out of bounds (underrun)\n"\
                 "undershot the tape size of %d cells." % TP_S)
    if RP >= TP_S: sys.exit("error: tape memory out of bounds (overrun)\n"\
                 "exceeded the tape size of %d cells." % TP_S)

def search_loop(IT):
    loop_lv = fdef_lv = 0
    loop_tp = [-1 for i in range(len(IT) + 1)]
    for i in range(len(IT)):
        char = IT[i]
        if char == '[':
            index = i
            cur_lv = loop_lv
            while index < len(IT):
                if IT[index] == '[': loop_lv += 1
                elif IT[index] == ']': loop_lv -= 1
                if IT[index] == ']' and loop_lv == cur_lv: break
                index += 1
            loop_tp[index] = i
            loop_tp[i] = index
        elif char == ']' and loop_tp[i] == -1:
            raise Exception("Loop not paired.")
        elif char == '(':
            index = i
            cur_lv = fdef_lv
            while index < len(IT):
                if IT[index] == '(': fdef_lv += 1
                elif IT[index] == ')': fdef_lv -= 1
                if IT[index] == ')' and fdef_lv == cur_lv: break
                index += 1
            loop_tp[index] = i
            loop_tp[i] = index

        elif char == ')' and not loop_tp[i]:
            raise Exception("Loop not paired.")
    return loop_tp

def execute(IT):                    # The instruction tape
    loop_tape = search_loop(IT)       # Store the loop objects
    old_IP = IP = loop_level = fdef_level = 0
    cur_refs = -1
    in_func = False
    while IP < len(IT):
        char = IT[IP]
        diff = 0
        if char in '-+':   add(int(char + '1'))
        elif char in '<>': mov(ord(char) - 61)
        elif char == '[': if cur_val() == 0: IP = loop_tape[IP]
        elif char == ']': if cur_val() != 0: IP = loop_tape[IP]
        elif char == '(':
            func_tape[cur_val()] = IP
            IP = loop_tape[IP]
        elif char == ')':
            if in_func:
                IP = old_IP
                in_func = False
        elif char == ':':
            print(func_tape[cur_val()])
            if not func_tape[cur_val()]:
                raise Exception("There is no such procedure.\n" + \
                        "Procedure reference (name) is: " + str(name))
            else:
                old_IP = IP
                in_func = True
                IP = func_tape[cur_val()]

        elif char == '#':
            print(loop_tape)
            low = 0 if RP < 5 else RP - 5
            high = TP_S if RP + 7 > TP_S else low + 13
            for index in range(low, high): print("%5d " % index, end='')
            print()
            for index in range(low, high): print("%5d " % RT[index], end='')
            print()
            for index in range(low, high):
                print("    ^ " if index == RP else "      ", end='')
            print()

        elif char == ',':
            if len(input_stream) == 0: input_stream += input()
            RT[RP] = ord(input_stream[0])
            input_stream = input_stream[1:]
        elif char == '.': putchar(cur_val())
        elif char == '@': reg = cur_val()
        elif char == '!': add(reg)
        IP += 1

def usage():
    print("""Usage: {prog} [OPTIONS] [file or code]
Options:
        -h      Show this help message
        -f file Use code from file

Use {prog} without arguments to open console
Use {prog} [code] to run code directly
""".format(prog=sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) == 3: if sys.argv[1] == '-f': run_file(sys.argv[2])
    if len(sys.argv) == 2:
        if sys.argv[1] == '-h':
            usage()
            sys.exit(0)
        if sys.argv[1] == '-f':
            print("No file specified.")
            sys.exit(2)
        else:
            execute(sys.argv[1])
            sys.exit(0)
    run_console()
