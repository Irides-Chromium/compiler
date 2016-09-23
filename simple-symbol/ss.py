#!/usr/bin/python3
TP_S = 30000

import sys, re
from putchar import putchar

OPER = "-+*/^%<>"   # "Operators"
RETN = "~#$:,(`"    # opers that return a value (an expr as well)
RECI = "~#$@:;.="   # opers that receive a value
BRAC = "{[()]}"     # The brackets

MX = [[0 for i in range(TP_S)] for i in range(8)]     # Array for tapes
TPS = [0, 0]                             # Tape Pointer Stack
#      ^ |^
#old_tape|new tape (current)
RPS = [0 for i in range(8)]              # Register Pointer Stack
expr_reg = 0
matchables = []
#stderr = open("ss_stderr.log", "w")
stderr = sys.stderr     # DEBUG

class brac_t:
    """
    Use for matchable structures: ()[]{}`` and ?...?!?$
    """
    pos_t = {"start": 0, "mid": 1, "end": 2}
    def __init__(self, byte, pos, val):
        """
        brac_t __init__(self, str byte, str pos, int val)
        `byte' is one of (, [, {, ? or ?[
        `pos' is one of 'start', 'mid', 'end'
        `val' is the index
        """
        self.byte = byte
        self.pos = self.pos_t[pos]
        self.indexes = [-1, -1, -1]
        self.indexes[self.pos] = val

    def __str__(self):
        types = ""
        return "<BYTE `{}' {} {} {}>".format(self.byte, \
                *["_" if i == -1 else i for i in self.indexes])
    
    def check_indexes(self):
        return self.indexes[0] < self.indexes[1] < self.indexes[2]

    def get_index(self):
        return self.indexes[self.pos]

    def set_index(self, pos, val):
        if val < 1: LOG(0, 1, "Index too low")
        self.indexes[self.pos_t[pos]] = val

    def get_other_end(self):
        if self.pos == 1: LOG(0, 1, "No such method for a `mid' type.")
        return self.indexes[2 - self.pos]

    def set_other_end(self, index):
        if index < 0: LOG(0, 1, "Index too low")
        if self.pos == 1: LOG(0, 1, "No such method for a `mid' type.")
        self.indexes[2 - self.pos] = index

    def matched(self):
        return True if self.get_other_end() else False

def get_val(index=-1):
    TP = TPS[1]
    RP = RPS[TP]
    # value = (32768 + value) % 65536 - 32768   # to simulate a `short int'
    return MX[TP][index or RP]

def set_val(value, index=-1):
    TP = TPS[1]
    RP = RPS[TP]
    # value = (32768 + value) % 65536 - 32768   # to simulate a `short int'
    MX[TP][index or RP] = value

def set_TP(tape_num):
    TPS.append(tape_num)
    TPS.pop(0)

def set_RP(index):
    if index < 0:
        LOG(0, 0, "tape index undershot the tape size of %d cells." % TP_S)
    if index >= TP_S: 
        LOG(0, 0, "tape index exceeded the tape size of %d cells." % TP_S)
    RPS[TPS[1]] = index

def move(diff):
    set_RP(RPS[TPS[1]] + diff)

def LOG(log_t, event_t, message):
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
    return retn

def equi(byte1, byte2):
    is_brac = BRAC.index(byte1) + BRAC.index(byte2) == 5
    is_cond = byte1 in "?!$" and byte2 in "?!$"
    return is_brac or is_cond or byte1 == byte2

def test(expr):
    """
    bool test(str expr)
    Used to eval the expression in a condition.
    """
    comp = expr[:2]
    expr = expr[2:]
    cur_val = get_val()
    val = parse_expr(expr)
    
    if comp == "<<": comp = "<"
    elif comp == ">>": comp = ">"

    return eval("{:d}{}{:d}".format(cur_val, comp, val))

def struct_scan(expr):
    """
    void struct_scan(str expr)
    Scan the structures of an expression.
    Raises Exceptions upon error.
    """
    global matchables
    matchables = [None for i in expr]
    unmatched = []
    IP = 0
    in_cond = 0
    while IP < len(expr):
        byte = expr[IP]
        print("BYTE::", byte)
        if byte in "([{":
            if in_cond == 2 and byte == "[":
                unmatched[-1][1] = byte = "?["
                in_cond -= 1
            matchables[IP] = brac_t(byte, "start", IP)
            unmatched += [(IP, byte)]
            print("UNMATCHED::", unmatched)
        elif byte in ")]}":
            start, struct_t = unmatched.pop()
            print("DEBUG")
            matchables[start].set_other_end(IP)
            matchables[IP] = brac_t(byte, "end", IP)
            matchables[IP].set_other_end(start)
            print("UNMATCHED::", unmatched)
        elif byte == '?':
            #if not bi_parsable(expr, IP + 1): LOG(0, 2, "Invalid syntax in conditional.")
            if expr[IP + 1] not in "!$":
                matchables[IP] = brac_t('?', "start", IP)
                unmatched += [(IP, byte)]
                in_cond = 2
            elif expr[IP + 1] == "!":
                start, struct_t = unmatched[-1]
                matchables[start].set_mid(IP)
                matchables[IP] = brac_t('?', "mid", IP)
                matchables[IP].set_start(start)
            else:
                start, struct_t = unmatched.pop()
                matchables[start].set_mid(IP)
                matchables[IP] = brac_t('?', "mid", IP)
                matchables[IP].start = start
        IP += 1
    return matchables

def parse(expr):
    IP = 0
    expr_reg_old = expr_reg
    expr_reg = 0
    while IP < len(expr):
        end_index = IP
        diff = bi_parsable(expr, IP)
        if diff: end_index += diff - 1
        else: break

def parse_expr(expr):
    expr_reg_old = expr_reg
    expr_reg = 0

def bi_parsable(expr, index):
    diff = 0
    if expr[index] == "?":
        bi_expr = expr[index:index + 4] 
        cond_t1 = re.compile("^\?((>=)|(==)|(<=)|(>>)|(<<)|(!=))[%s]$" % RETN)
        cond_t2 = re.compile("^\?[!$]$")
        if cond_t1.match(bi_expr) or cond_t2.match(bi_expr): diff = 4
    else:
        bi_expr = expr[index:index + 2]
        reci_t = re.compile("[%s%s][%s]" % (RECI, OPER, RETN))
        # Bi-parsing type of oper that receive an param
        oper_t = re.compile("[%s][^%s]")
        # no two successive opers can be parsed
        if oper_t.match(bi_expr) or reci_t.match(bi_expr): diff = 2
    return diff

def get_parsable_index(expr):
    index = 0
    while index < len(expr):
        diff = bi_parsable(expr, index)
        if diff: index += diff - 1
        else: break
    return index

def bi_eval(oper, param):
    """
    bi_eval(char oper, int param) -> operation/value
    Parse these opers:
    ~ # @ $ % ^ ! * + - < > : ; , . = /
    Bi-parsing is applicable to these opers.
    """
    is_oper = True if param else False
    if oper in OPER: exec("set_val(get_val() %c %d)" % (oper, param or 2))
    elif oper == "~":
        if is_oper:
            LOG(3, 0, "Tape number requested: %d" % param)
            if param > 7 or param < 0:
                LOG(0, 0, "Tape number out of range.")
            tape_num = param
        else: return TPS[1]
    elif oper == "#": 
        if is_oper: set_RP(param)
        else: return RPS[TPS[1]]
    elif oper == "@": MX[RPS[TPS[0]]] += param or get_val()
    elif oper == "$":
        if not param: return get_val()
        if param == -1: return expr_reg_old
        # Expression cell
        return get_val(param)
    elif oper == "!": 
        MX[TP] += param or MX[other_tape]
    elif oper in "<>": RP += (ord(oper) - 61) * param
    elif oper == ":":
        old_RP = RP
        RP = param if param else RP
        retn = ss_eval(FT[get_val()])
        RP = old_RP
        return retn
    elif oper == ";": return param or get_val()
    elif oper == ",": return getchar()
    elif oper == ".": putchar(param or get_val())
    elif oper == "=": sys.exit(param or get_val())

    return 0
