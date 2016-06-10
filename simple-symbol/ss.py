#!/usr/bin/python3
TP_S = 30000

MX = [[0 for i in range(TP_S)] for i in range(8)]     # Array for tapes
TPS = [0, 0]                             # Tape Pointer Stack
#      ^  ^
#old_tape new tape (current)
RPS = [0 for i in range(8)]              # Register Pointer Stack

def get_val(index=-1):
    TP = TPS[1]
    RP = RPS[TP]
    index = (index + 1 or RP + 1) - 1
    # value = (32768 + value) % 65536 - 32768   # to simulate a `short int`
    return MX[TP][index]

def set_val(value, index=-1):
    TP = TPS[1]
    RP = RPS[TP]
    index = (index + 1 or RP + 1) - 1
    # value = (32768 + value) % 65536 - 32768   # to simulate a `short int`
    MX[TP][index] = value

def set_TP(tape_num):
    TPS.append(tape_num)
    TPS.pop(0)

def set_RP(index):
    if index < 0: sys.exit("error: tape memory out of bounds (underrun)\n"\
                    "undershot the tape size of %d cells." % TP_S)
    if index >= TP_S: 
        ys.exit("error: tape memory out of bounds (overrun)\n"\
                 "exceeded the tape size of %d cells." % TP_S)
    RPS[TPS[1]] = index

def move(diff):
    set_RP(RPS[TPS[1]] + diff)

def bi_eval(operator, operand, oper_type):
    """Parse these operators:
    ~ # @ $ % ^ ! * + < > : ; , . = ? /
    Bi-parsing  is applicable to these operators.
    """
    if operator in '+-*/^%':
        eval("set_val(get_val() %c operand)" % operator)
    elif operator == '~':
        if oper_type:
            if operand > 7 or operand < 0:
                sys.exit("Tape number out of range." \
                         "Requested index: %d" % operand)
            tape_num = operand
        else: return TPS[1]
    elif operator == '#': 
        if oper_type: set_RP(operand)
        else: return RPS[TPS[1]]
    elif operator == '@':
        MX[RPS[TPS[0]]] += operand or get_val()
    elif operator == '$':
        return get_val(operand) or get_val()
    elif operator == '!': 
        MX[TP] += operand or MX[other_tape]
    elif operator in '<>': RP += (ord(operator) - 61) * operand
    elif operator == ':':
        old_RP = RP
        RP = operand if operand else RP
        retn = ss_eval(FT[get_val()])
        RP = old_RP
        return retn
    elif operator == ';': return operand or get_val()
    elif operator == '.': putchar(operand or get_val())
    elif operator == '=': sys.exit(operand or get_val())

    return None
