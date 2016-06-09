#!/usr/bin/python3

MX = [[0 for i in range(30000)] for i in range(8)]     # Array for tapes
TPS = [0, 0]                             # Tape Pointer Stack
#      ^  ^
#old_tape new tape (current)
RPS = [0 for i in range(8)]              # Register Pointer Stack

def get_val(index=-1):
    TP = TPS[1]
    RP = RPS[TP]
    index = (index + 1 or RP + 1) - 1
    return MX[TP][index]

def set_val(value, index=-1):
    TP = TPS[1]
    RP = RPS[TP]
    index = (index + 1 or RP + 1) - 1
    MX[TP][index] = value

def set_TP(tape_num):
    TPS.append(tape_num)
    TPS.pop(0)

def set_RP(index):
    RPS[TPS[1]] = index

def bi_eval(operator, operand, oper_type):
    if operator in '~#@$%^!*+-<>:;.=/':
        if operator in '+-*/^%':
            eval("MX[TP][RP] %c= operand" % operator)
        elif operator == '~':
            if oper_type: tape_num = operand
            else: return TP
        elif operator == '#': 
            if oper_type: RP = operand
            else: return RP
        elif operator == '@':
            MX[other_tape] += operand or MX[TP]
        elif operator == '$':
            return MX[TP][operand] or cur_val()
        elif operator == '!': 
            MX[TP] += operand or MX[other_tape]
        elif operator in '<>': RP += (ord(operator) - 61) * operand
        elif operator == ':':
            old_RP = RP
            RP = operand if operand else RP
            retn = ss_eval(ss_inst(FT[cur_val()]))
            RP = old_RP
            return retn
        elif operator == ';': return operand or cur_val()
        elif operator == '.': putchar(operand or cur_val())
        elif operator == '=': sys.exit(operand or cur_val())

        return None
