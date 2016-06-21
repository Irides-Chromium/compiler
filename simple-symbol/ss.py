#!/usr/bin/python3
TP_S = 30000

import sys, re
from putchar import putchar

MX = [[0 for i in range(TP_S)] for i in range(8)]     # Array for tapes
TPS = [0, 0]                             # Tape Pointer Stack
#      ^  ^
#old_tape new tape (current)
RPS = [0 for i in range(8)]              # Register Pointer Stack
expr_reg = 0

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
    if index < 0:
        sys.exit(log(0, 0, \
                "tape index undershot the tape size of %d cells." % TP_S))
    if index >= TP_S: 
        sys.exit(log(0, 0, \
                "tape index exceeded the tape size of %d cells." % TP_S))
    RPS[TPS[1]] = index

def move(diff):
    set_RP(RPS[TPS[1]] + diff)

def log(log_t, event_t, message):
    log = "FWDIV"
    # Fatal, Error, Warning, Debug, Info, Verbose
    return_val = "32"
    event = ["MEM Management", "Brackets", "Expression"]
    print("".join((log[log_t], "/[", event[event_t], "]: ", message)), \
            file=sys.stderr)
    return int(return_val[log_t])

def parse(expr):
    IP = 0
    expr_reg_old = expr_reg
    expr_reg = 0
    while IP < len(expr):
        byte = expr[IP]
        while IP < len(expr) and parsable(expr, IP):
                bi_eval(byte, expr[IP + 1], True)

def parse_expr(expr):
    expr_reg_old = expr_reg
    expr_reg = 0

def parsable(expr, index):
    oper = "+-*/^%"     # "Operators"
    retn = "~#$:,("     # operators that return a value (an expr as well)
    reci = "~#$@<>:;.=" # operators that receive a value
    brac = "(){}[]"     # The brackets
    match = None
    if expr[index - 1] == "?":
        bi_expr = expr[index - 1:index + 3] 
        cond_t = re.compile("^\?((>=)|(==)|(<=)|(\?>)|(\?<))[%s]$" % retn)
        match = cond_t.match(bi_expr)
    else:
        expr[index - 1:index + 1]
        oper_t = re.compile("[%s][%s]" % (oper, retn))
        reci_t = re.compile("[%s][%s]" % (reci, retn))
        match = oper_t.match(bi_expr) or reci_t.match(bi_expr)
    return True if match else False

def bi_eval(operator, operand, is_operator):
    """
    Parse these operators:
    ~ # @ $ % ^ ! * + - < > : ; , . = /
    Bi-parsing is applicable to these operators.
    """
    if operator in "+-*/^%":
        eval("set_val(get_val() %c operand)" % operator)
    elif operator == "~":
        if is_operator:
            log(3, 0, "Tape number requested: %d" % operand)
            if operand > 7 or operand < 0:
                sys.exit(log(0, 0, "Tape number out of range."))
            tape_num = operand
        else: return TPS[1]
    elif operator == "#": 
        if is_operator: set_RP(operand)
        else: return RPS[TPS[1]]
    elif operator == "@":
        MX[RPS[TPS[0]]] += operand or get_val()
    elif operator == "$":
        return get_val(operand) if operand else get_val()
    elif operator == "!": 
        MX[TP] += operand or MX[other_tape]
    elif operator in "<>": RP += (ord(operator) - 61) * operand
    elif operator == ":":
        old_RP = RP
        RP = operand if operand else RP
        retn = ss_eval(FT[get_val()])
        RP = old_RP
        return retn
    elif operator == ";": return operand or get_val()
    elif operator == ",": return getchar()
    elif operator == ".": putchar(operand or get_val())
    elif operator == "=": sys.exit(operand or get_val())

    return None
