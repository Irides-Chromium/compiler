#!/usr/bin/python3

import time
import sys

def run_console():
    print("Use # to inspect tape")
    environment = bf_prog()
    while True:
        try:
            instruction = bf_inst(input(">>> "))
            instruction.execute(environment)
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)

def run_file(filename):
    try:
        file = open(filename, "r")
    except IOError:
        print("%s: cannot find %s: no such file" % (sys.argv[0], filename))
        sys.exit(2)
    else:
        environment = bf_prog()
        instruction = bf_inst(file.read())
        instruction.execute(environment)

def getchar():
    if len(input_stream) == 0:
        input_stream += input()
    temp = input_stream[0]
    input_stream = input_stream[1:]
    return ord(temp)

def putchar(char):
    print(chr(char), end='')

class bf_prog:

    tape_size = 4096

    def __init__(self):
        self.input_stream = ""
        self.regs_tape = []
        self.RP = 0              # Register Pointer
        for i in range(bf_prog.tape_size):
            self.regs_tape.append(0)

    def __str__(self):
        return '(' + ', '.join((str(self.RP), str(self.cur_val()))) + ')'

    def cur_val(self):
        return self.regs_tape[self.RP]

    def add(self, value):
        self.regs_tape[self.RP] += value
        self.regs_tape[self.RP] %= 256

    def move(self, diff):
        self.RP += diff
        if self.RP < 0:
            sys.exit("error: tape memory out of bounds (underrun)\n\
                      undershot the tape size of 30000 cells")
        if self.RP > self.tape_size:
            sys.exit("error: tape memory out of bounds (underrun)\n\
                      undershot the tape size of 30000 cells")

    def handle_input(self):
        self.regs_tape[self.RP] = getchar()

    def handle_output(self):
        putchar(self.regs_tape[self.RP])

class bf_loop:
    
    def __init__(self, level, start):
        self.loop_start = start
        self.loop_end = start
        self.level = level
        self.paired = False

    def set_end(self, end):
        self.loop_end = end
        self.paired = True

    def may_match(self, level, index):
        level_match = self.level == level
        start_first = self.loop_start < index
        return level_match and not self.paired and start_first

    def __str__(self):
        return '(' + ', '.join((str(self.loop_start), str(self.loop_end), str(self.level), str(self.paired))) + ')'

class bf_inst:

    def __init__(self, tape):
        self.inst_tape = tape
        self.loop_tape = []      # Storing the loop objects
        self.IP = 0              # Instruction Pointer
        self.search_loop()

    def __str__(self):
        return self.inst_tape

    def search_loop(self):
        ptr = 0
        level = 0
        for ptr in range(len(self.inst_tape)):
            if self.inst_tape[ptr] == '[':
                self.loop_tape.append(bf_loop(level, ptr))
                level += 1
            elif self.inst_tape[ptr] == ']':
                level -= 1
                paired = False
                for loop in self.loop_tape:
                    if loop.may_match(level, ptr):
                        loop.set_end(ptr)
                        paired = True
                        break
                if not paired:
                    #print("level, *ptr, paired:", level, self.inst_tape[ptr], paired)
                    #for loop in self.loop_tape:
                        #print(loop)
                    raise Exception("Loop end \"]\" not paired.")

        for loop in self.loop_tape:
            if not loop.paired:
                raise Exception("Loop not paired.")

    def execute(self, env):
        self.IP = 0
        while self.IP < len(self.inst_tape):
            char = self.inst_tape[self.IP]
            diff = 0
            if char in '-+':
                while (self.IP < len(self.inst_tape) \
                        and self.inst_tape[self.IP] in '-+'):
                    char = self.inst_tape[self.IP]
                    if char == '+':
                        diff += 1
                    else:
                        diff -= 1
                    self.IP += 1
                self.IP -= 1
                env.add(diff)

            elif char in '<>':
                while (self.IP < len(self.inst_tape) \
                        and self.inst_tape[self.IP] in '<>'):
                    char = self.inst_tape[self.IP]
                    if char == '>':
                        diff += 1
                    else:
                        diff -= 1
                    self.IP += 1
                self.IP -= 1
                env.move(diff)

            elif char == ',':
                env.handle_input()
            elif char == '.':
                env.handle_output()

            elif char == '[':
                start = 0
                end = 0
                for loop in self.loop_tape:
                    if loop.loop_start == self.IP:
                        start = loop.loop_start
                        end = loop.loop_end
                        break
                if env.cur_val() != 0:
                    self.IP = end
                    #print("end:", self.inst_tape[self.IP])
                    inst = bf_inst(self.inst_tape[start + 1:end])
                    while env.cur_val() != 0:
                        inst.execute(env)
                        #print("inst:", inst)
                    #print("regs:", env)

            elif char == '#':
                low = env.RP - 10
                if env.RP < 10:
                    low = 0
                high = low + 20
                if env.RP + 10 > bf_prog.tape_size:
                    high = 4095
                for index in range(low, high):
                    print("%03d " % index, end='')
                print()
                for index in range(low, high):
                    print("%03d " % env.regs_tape[index], end='')
                print()
                for index in range(low, high):
                    if index == env.RP:
                        print("^   ", end='')
                    else:
                        print("    ", end='')
                print()

            elif char == ']':
                raise Exception("LOOP END ENCOUNTERED")

            self.IP += 1

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_console()
