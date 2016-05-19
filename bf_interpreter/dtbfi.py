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

# This version uses: 
# 1. Original features of brainfuck
# 2. Two-tape extension
# 3. 2 byte storage (65536) for each cell
# 4. Number repeat macro
# 5. Wrapped tape and 
# 6. Quit extension
# Avaliable operators:
# + - [ ] < > , . ( ) : @ ! ~ = 1 2 3 4 5 6 7 8 9 0

# Mutiply:
# num1  num2  result
# ^start      ^end
# [->[->+>+<<]>>[-<<+>>]<<<]>[-]>

# Division
# number 0 divisor
# [->+>-[>+>>]>[+[-<+>]>+>>]<<<<<<]
# 0 number d-n%d n%d n/d

import time
import sys

CL_S = 65536       # the maximum number allowed + 1
TP_S = 30000       # count of cells

def run_console():
    print("Brainfuck Interpreter 1.0.2 (with pbrain)")
    print("Use '#' to inspect tape")
    environment = bf_prog()
    while True:
        try: bf_inst(input(">>> ")).execute(environment)
        except (EOFError, KeyboardInterrupt): sys.exit(print())

def run_file(filename):
    try: file = open(filename, "r")
    except IOError: sys.exit("%s: cannot find %s: no such file" % \
            (sys.argv[0], filename))
    else: bf_inst(file.read()).execute(bf_prog())

class bf_prog:
    """The environment or context used by the BF program.
    Created only once in every file or console."""

    def __init__(self):
        self.input_stream = ""
        self.RT_A = []                  # Register tape (paper tape)
        self.RT_B = []
        self.RT = [self.RT_A, self.RT_B]
        self.RP_A = 0                   # Register Pointer
        self.RP_B = 0
        self.RP = [self.RP_A, self.RP_B]
        self.CT = 0                     # Current Tape number
        self.func_tape = []             # Function tape (for '(' ')' ':')
        for i in range(CL_S):
            self.func_tape.append(None) # Initialize function tape
        for i in range(TP_S):
            self.RT_A.append(0)         # Initialize register tape
            self.RT_B.append(0)

    def __str__(self):
        return "@%d: %d, @%d: %d" % (self.RP[0], self.get_val(0), \
                                     self.RP[1], self.get_val(1))

    def get_val(self, this=True):
        tape = self.CT if this else 1 - self.CT
        return self.RT[tape][self.RP[tape]]

    def add(self, value, this=True):
        tape = self.CT if this else 1 - self.CT
        self.RT[tape][self.RP[tape]] += value
        self.RT[tape][self.RP[tape]] %= CL_S

    def move(self, diff):
        self.RP[self.CT] += diff
        self.RP[self.CT] %= 30000

    def handle_i(self):
        if len(self.input_stream) == 0:
            self.input_stream += input()
        self.RT[self.CT][self.RP[self.CT]] = ord(self.input_stream[0])
        self.input_stream = self.input_stream[1:]

    def handle_o(self):
        print(chr(self.get_val()), end='')

    def set_reg(self):                  # Set value to the other tape
        self.add(self.get_val(), False)

    def ext_reg(self):                  # Extract value from the other tape
        self.add(self.get_val(False))

    def switch_tape(self):
        self.CT = 1 - self.CT

class bf_loop:
    """Class for matching '[' ']' and '(' ')'s.
    Not necessarily used for loops."""
    
    def __init__(self, level, start):
        self.loop_end = self.loop_start = start
        self.level = level
        self.paired = False

    def set_end(self, end):
        self.loop_end = end
        self.paired = True

    def match(self, level, index):
        return self.level == level \
                and not self.paired \
                and self.loop_start < index

    def __str__(self):
        return '(' + ', '.join((str(self.loop_start), str(self.loop_end), \
                str(self.level), str(self.paired))) + ')'

class bf_inst:
    """Represent one string of instruction in the program.
    When encounter loops and definitions, use a new instruction instead.
    Jump to the next byte (operator) after the loop or definition."""

    def __init__(self, tape):
        self.IT = tape              # The instruction tape
        self.loop_tape = []         # Store the loop objects
        self.fdef_tape = []         # Store Function definition start & end
        self.IP = 0                 # Instruction Pointer
        self.search_loop()          # Store the loop pairs for future use

    def __str__(self):
        return self.IT

    def next(self):                 # Move IP to the next one
        self.IP += 1

    def prev(self):                 # Move IP to the previous one
        self.IP -= 1

    def get_oper(self):             # The operator at the current position
        return self.IT[self.IP]

    def search_loop(self):
        loop_level = fdef_level = 0
        for ptr in range(len(self.IT)):
            char = self.IT[ptr]
            if char in '([':
                level = loop_level if char == '[' else fdef_level
                tape = self.loop_tape if char == '[' else self.fdef_tape
                tape.append(bf_loop(level, ptr))
                if char == '[': loop_level += 1
                else:           fdef_level += 1

            elif char in '])':
                level = tape = 0
                if char == ')':
                    fdef_level -= 1
                    level, tape = fdef_level, self.fdef_tape
                else:
                    loop_level -= 1
                    level, tape = loop_level, self.loop_tape
                paired = False
                for loop in tape:
                    if loop.match(level, ptr):
                        loop.set_end(ptr)
                        paired = True
                        break
                if not paired:
                    raise Exception("Loop not paired." \
                            "(char: %s, pos: %d)" % (char, ptr))

        for tape in (self.fdef_tape, self.loop_tape):
            for loop in tape:
                if not loop.paired:
                    raise Exception("Loop not paired.")

    def execute(self, env):
        self.IP = 0
        while self.IP < len(self.IT):
            char = self.get_oper()
            diff = 0
            if char in '-+':
                while (self.IP < len(self.IT) and self.get_oper() in '-+'):
                    char = self.get_oper()
                    diff += 1 if char == '+' else -1
                    self.next()
                self.prev()
                env.add(diff)

            elif char in '<>':
                while (self.IP < len(self.IT) and self.get_oper() in '<>'):
                    char = self.get_oper()
                    diff += 1 if char == '>' else -1
                    self.next()
                self.prev()
                env.move(diff)

            elif char in '([':
                start = end = 0
                tape = self.loop_tape if char == '[' else self.fdef_tape
                for loop in tape:
                    if loop.loop_start == self.IP:
                        start, end = loop.loop_start, loop.loop_end
                        break
                self.IP = end

                if char == '[':
                    if env.get_val() != 0:
                        inst = bf_inst(self.IT[start + 1:end])
                        while env.get_val() != 0:
                            inst.execute(env)
                else:
                    env.func_tape[env.get_val()] = \
                            bf_inst(self.IT[start + 1:end])

            elif char == ':':
                name = env.get_val()
                if not env.func_tape[name]:
                    raise Exception("There is no such procedure.\n" + \
                            "Procedure reference is: " + str(name))
                env.func_tape[name].execute(env)
# DEBUG USE
#           elif char in '])':
#               raise Exception("LOOP END ENCOUNTERED: at " + str(self.IP) \
#                       + "\n" + self.IT[self.IP - 5:self.IP + 6] \
#                       + "\n" + "     ^")

            elif char == '#':
                print("Current tape: %d" % (env.CT + 1))
                for tape_num in [0, 1]:
                    print("Tape number: %d" % (tape_num + 1))
                    ptr = env.RP[tape_num]
                    lo = ptr - 5
                    hi = ptr + 7
                    for index in range(lo, hi):
                        print("%5d " % (index % TP_S), end='')
                    print()
                    for index in range(lo, hi):
                        print("%5d " % env.RT[tape_num][index % TP_S], \
                                end='')
                    print()
                    for index in range(lo, hi):
                        if index == ptr:
                            print("    ^ ", end='')
                        else:
                            print("      ", end='')
                    print()

            elif char.isdigit():
                temp = ""
                while (self.IP < len(self.IT) and \
                        self.get_oper().isdigit()):
                    temp += self.get_oper()
                    self.next()
                diff = int(temp)
                char = self.get_oper()
                if char == '+':
                    env.add(diff)
                elif char == '-':
                    env.add(-diff)
                elif char == '>':
                    env.move(diff)
                elif char == '<':
                    env.move(-diff)
                elif char == ',':
                    for i in range(diff):
                        env.handle_i()
                elif char == '.':
                    for i in range(diff):
                        env.handle_o()
                else:
                    self.prev()

            elif char == ',':
                env.handle_i()
            elif char == '.':
                env.handle_o()
            elif char == '@':
                env.set_reg()
            elif char == '!':
                env.ext_reg()
            elif char == '~':
                env.switch_tape()
            elif char == '=':
                sys.exit(env.get_val())

            self.next()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_console()
