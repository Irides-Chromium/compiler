#!/usr/bin/python3
TP_S = 30000

import sys, re
from putchar import putchar

OPER = "-+*/^%<>"   # "Operators"
RETN = "~#$:,("     # operators that return a value (an expr as well)
RECI = "~#$@:;.="   # operators that receive a value
BRAC = "{[()]}"     # The brackets

MX = [[0 for i in range(TP_S)] for i in range(8)]     # Array for tapes
TPS = [0, 0]                             # Tape Pointer Stack
#      ^  ^
#old_tape new tape (current)
RPS = [0 for i in range(8)]              # Register Pointer Stack
expr_reg = 0
matchables = []
stderr = open("ss_stderr.log", "w")

class brac_t:       # Use for matchable structures: ()[]{} and ?...?!?$
    pos_t = ["mid", "end", "start"]
    #         0      1      -1
    def __init__(self, struct_type, start=-1, mid=-1, end=-1):
        self.struct_t = struct_type     # (, [, {, or ?
        for pos in pos_t:
            exec("self.{p} = {p}".format(p=pos)
        self.pos = -1
        if mid >= 0:
            self.pos = 0
        elif end >= 0:
            self.pos = 1

    def set_mid(self, mid):
        if mid < 1:
            log(0, 1, "Index too low")
        self.mid = mid

    def set_other_end(self, other_end):
        if other_end < 1: log(0, 1, "Index too low")
        if self.pos == 0: log(0, 1, "No such method for a `mid' type.")
        exec("self.{} = {}".format(pos_t[-self.pos], other_end))

    def matched(self):
        return True if self.get_other_end() else False

    def get_other_end(self):
        if self.pos == 0: log(0, 1, "No such method for a `mid' type.")
        return eval("self.{}".format(pos_t[-self.pos]))

def get_val(index=-1):
    TP = TPS[1]
    RP = RPS[TP]
    index = index or RP
    # value = (32768 + value) % 65536 - 32768   # to simulate a `short int'
    return MX[TP][index]

def set_val(value, index=-1):
    TP = TPS[1]
    RP = RPS[TP]
    index = index or RP
    # value = (32768 + value) % 65536 - 32768   # to simulate a `short int'
    MX[TP][index] = value

def set_TP(tape_num):
    TPS.append(tape_num)
    TPS.pop(0)

def set_RP(index):
    if index < 0:
        log(0, 0, "tape index undershot the tape size of %d cells." % TP_S)
    if index >= TP_S: 
        log(0, 0, "tape index exceeded the tape size of %d cells." % TP_S)
    RPS[TPS[1]] = index

def move(diff):
    set_RP(RPS[TPS[1]] + diff)

def log(log_t, event_t, message):
    log = "FWDIV"
    # Fatal, Warning, Debug, Info, Verbose
    return_val = "32000"
    event = ["MEM Management", "Brackets", "Expression"]
    print("".join((log[log_t], "/[", event[event_t], "]: ", message)), \
            file=stderr)
    retn = int(return_val[log_t])
    if retn > 0:
        if stderr != sys.stderr: stderr.close()
        sys.exit(retn)

def equi(byte1, byte2):
    is_brac = BRAC.index(byte1) + BRAC.index(byte2) == 5
    is_cond = byte1 in "?!$" and byte2 in "?!$"
    return is_brac or is_cond or byte1 == byte2

def struct_scan(expr):
    global matchables
    matchables = [None for i in expr]
    unmatched = []
    IP = 0
    in_cond = False
    while IP < len(expr):
        byte = expr[IP]
        if byte in "([{":
            if in_cond and byte == "[":
                unmatched[-1][1] = "?["
            matchables[IP] = brac_t(byte, start=IP)
            unmatched += [(IP, byte)]
        elif byte in ")]}":
            start, struct_t = unmatched.pop()
            matchables[start].set_other_end(IP)
            matchables[IP] = brac_t(byte, end=IP)
            matchables[IP].set_other_end(start)
        elif byte == '?':
            if not parsable(expr, IP + 1):
                log(0, 2, "Invalid syntax in conditional.")
            if expr[IP + 1] not in "!$":
                matchables[IP] = brac_t('?', start=IP)
                unmatched += [(IP, byte)]
                in_cond = True
            elif expr[IP + 1] == "!":
                start, struct_t = unmatched[-1]
                matchables[start].set_mid(IP)
                matchables[IP] = brac_t('?', mid=IP)
                matchables[IP].start = start
                matchables[start].set_mid(IP)
            else:
                start, struct_t = unmatched[-1]
                matchables[start].set_mid(IP)
                matchables[IP] = brac_t('?', mid=IP)
                matchables[IP].start = start
                matchables[start].set_mid(IP)

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
    match = None
    if expr[index - 1] == "?":
        bi_expr = expr[index - 1:index + 3] 
        cond_t1 = re.compile("^\?((>=)|(==)|(<=)|(\?>)|(\?<))[%s]$" % RETN)
        cond_t2 = re.compile("^\?[!$]$")
        match = cond_t1.match(bi_expr) or cond_t2.match(bi_expr)
    else:
        expr[index - 1:index + 1]
        reci_t = re.compile("[%s%s][%s]" % (RECI, OPER, RETN))
        # Bi-parsing type of operator that receive an operand
        oper_t = re.compile("[%s][^%s]")
        # no two successive operators can be parsed
        match = oper_t.match(bi_expr) or reci_t.match(bi_expr)
    return True if match else False

def bi_eval(operator, operand, is_operator):
    """
    Parse these operators:
    ~ # @ $ % ^ ! * + - < > : ; , . = /
    Bi-parsing is applicable to these operators.
    """
    if operator in OPER:
        eval("set_val(get_val() %c operand)" % operator)
    elif operator == "~":
        if is_operator:
            log(3, 0, "Tape number requested: %d" % operand)
            if operand > 7 or operand < 0:
                log(0, 0, "Tape number out of range.")
            tape_num = operand
        else: return TPS[1]
    elif operator == "#": 
        if is_operator: set_RP(operand)
        else: return RPS[TPS[1]]
    elif operator == "@":
        MX[RPS[TPS[0]]] += operand or get_val()
    elif operator == "$":
        if not operand:
            return get_val()
        if operand == -1:           # Expression cell
            return expr_reg_old
        return get_val(operand)
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

    return 0
