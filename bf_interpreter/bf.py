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

import time
import sys
from get_options import read_opts

CL_S, TP_S, TP_W, TM_R, DB_T, RP_M, EX_Q = read_opts()

def run_console():
    print("Brainfuck Interpreter 1.0.2 (with pbrain)")
    print("Use '#' to inspect tape")
    environment = bf_prog()
    while True:
        try:
            bf_inst(input(">>> ")).execute(environment)
        except (EOFError, KeyboardInterrupt):
            sys.exit(print())

def run_file(filename):
    try:
        file = open(filename, "r")
    except IOError:
        print("%s: cannot find %s: no such file" % (sys.argv[0], filename))
        sys.exit(2)
    else:
        bf_inst(file.read()).execute(bf_prog())

class bf_prog:
    """The environment or context used by the BF program.
    Created only once in every file or console."""

    def __init__(self):
        self.input_stream = ""
        self.RT = []                    # Register tape (paper tape)
        self.RP = 0                     # Register Pointer
        self.func_tape = []             # Function tape (for '(' ')' ':')
        self.reg = 0                    # Temporary register
        for i in range(CL_S):
            self.func_tape.append(None) # Initialize function tape
        for i in range(TP_S):
            self.RT.append(0)           # Initialize register tape

    def __str__(self):
        return '(' + ', '.join((str(self.RP), str(self.cur_val()))) + ')'

    def cur_val(self):
        return self.RT[self.RP]

    def add(self, value):
        self.RT[self.RP] += value
        self.RT[self.RP] %= CL_S

    def move(self, diff):
        self.RP += diff
        if self.RP < 0:
            sys.exit("error: tape memory out of bounds (underrun)\n" \
                     "undershot the tape size of %d cells." % TP_S)
        if self.RP >= TP_S:
            sys.exit("error: tape memory out of bounds (overrun)\n" \
                     "undershot the tape size of %d cells." % TP_S)

    def handle_input(self):
        if len(self.input_stream) == 0:
            self.input_stream += input()
        self.RT[self.RP] = ord(self.input_stream[0])
        self.input_stream = self.input_stream[1:]

    def handle_output(self):
        print(chr(self.RT[self.RP]), end='')

    def set_reg(self):
        self.reg = self.cur_val()

    def ext_reg(self):          # Extract value from the temporary register
        self.add(self.reg)

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

    def search_loop(self):
        ptr = loop_level = fdef_level = 0
        for ptr in range(len(self.IT)):
            if self.IT[ptr] == '[':
                self.loop_tape.append(bf_loop(loop_level, ptr))
                loop_level += 1
            elif self.IT[ptr] == ']':
                loop_level -= 1
                paired = False
                for loop in self.loop_tape:
                    if loop.match(loop_level, ptr):
                        loop.set_end(ptr)
                        paired = True
                        break
                if not paired:
                    raise Exception("Loop end ']' not paired.")

            elif self.IT[ptr] == '(':
                self.fdef_tape.append(bf_loop(fdef_level, ptr))
                fdef_level += 1
            elif self.IT[ptr] == ')':
                fdef_level -= 1
                paired = False
                for loop in self.fdef_tape:
                    if loop.match(fdef_level, ptr):
                        loop.set_end(ptr)
                        paired = True
                        break
                if not paired:
                    raise Exception("Function definition not ended ')' .")

        for loop in self.fdef_tape:
            if not loop.paired:
                raise Exception("Loop not paired.")
        for loop in self.loop_tape:
            if not loop.paired:
                raise Exception("Loop not paired.")

    def execute(self, env):
        self.IP = 0
        while self.IP < len(self.IT):
            char = self.IT[self.IP]
            diff = 0
            #print(char, char.isdigit())
            if char in '-+':
                while (self.IP < len(self.IT) and self.IT[self.IP] in '-+'):
                    char = self.IT[self.IP]
                    if char == '+': diff += 1
                    else:           diff -= 1
                    self.IP += 1
                self.IP -= 1
                env.add(diff)

            elif char in '<>':
                while (self.IP < len(self.IT) \
                        and self.IT[self.IP] in '<>'):
                    char = self.IT[self.IP]
                    if char == '>': diff += 1
                    else:           diff -= 1
                    self.IP += 1
                self.IP -= 1
                env.move(diff)

            elif char == '[':
                start = end = 0
                for loop in self.loop_tape:
                    if loop.loop_start == self.IP:
                        start, end = loop.loop_start, loop.loop_end
                        break
                self.IP = end
                if env.cur_val() != 0:
                    inst = bf_inst(self.IT[start + 1:end])
                    while env.cur_val() != 0:
                        inst.execute(env)

            elif char == '(':
                start = end = 0
                for loop in self.fdef_tape:
                    if loop.loop_start == self.IP:
                        start, end = loop.loop_start, loop.loop_end
                        break
                self.IP = end
                
                env.func_tape[env.cur_val()] = \
                        bf_inst(self.IT[start + 1:end])

            elif char == ':':
                name = env.cur_val()
                if not env.func_tape[name]:
                    raise Exception("There is no such procedure.\n" + \
                            "Procedure reference " + \
                            "(name) is: " + str(name))
                env.func_tape[name].execute(env)

            elif char in '])':
                raise Exception("LOOP END ENCOUNTERED: at " + str(self.IP) \
                        + "\n" + self.IT[self.IP - 5:self.IP + 6] \
                        + "\n" + "   ^")

            elif char == '#':
                low = 0 if env.RP < 10 else env.RP - 10
                high = TP_S - 1 if env.RP + 10 > TP_S else low + 20
                for index in range(low, high):
                    print("%3d " % index, end='')
                print()
                for index in range(low, high):
                    print("%3d " % env.RT[index], end='')
                print()
                for index in range(low, high):
                    if index == env.RP:
                        print("  ^ ", end='')
                    else:
                        print("    ", end='')
                print()

            elif RP_M and char.isdigit():
                temp = ""
                while (self.IP < len(self.IT) and \
                        self.IT[self.IP].isdigit()):
                    temp += self.IT[self.IP]
                    self.IP += 1
                diff = int(temp)
                char = self.IT[self.IP]
                if char == '+':
                    env.add(diff)
                elif char == '-':
                    env.add(-diff)
                elif char == '<':
                    env.move(-diff)
                elif char == '>':
                    env.move(diff)
                elif char == ',':
                    for i in range(diff):
                        env.handle_input()
                elif char == '.':
                    for i in range(diff):
                        env.handle_output()

            elif char == ',':
                env.handle_input()
            elif char == '.':
                env.handle_output()
            elif TM_R:
                if char == '@':
                    env.set_reg()
                elif char == '!':
                    env.ext_reg()
            elif char == '=':
                sys.exit(env.cur_val())

            self.IP += 1

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_console()
