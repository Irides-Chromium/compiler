#!/usr/bin/python3
TP_S = 1024

import sys, re
from putchar import putchar

OPER = "-+*/^%<>"   # "Operators"
RETN = "~#$:,(`"    # opers that return a value (an expr as well)
RECI = "~#$@:;.="   # opers that receive a value
BRAC = "{[()]}"     # The brackets
L_BRAC = "{[("
R_BRAC = ")]}"
#stderr = open("ss_stderr.log", "w")
stderr = sys.stderr         # DEBUG

class Env:

    def __init__(self):

        self.MX = [[0 for i in range(TP_S)] for i in range(4)]
        # Array for tapes
        self.TPS = [0, 0]                # Tape Pointer Stack
        #      ^ |^
        #old tape|new tape (current)
        self.RPS = [0, 0, 0, 0] # Register Pointer Stack
        self.expr_tape = ExprTape()
        self.FT = {}            # Function Reference
        #self.structs = []

    def get_type(self): return "Env"

    def get_val(self, index=None, cur=True):
        return self.MX[self.get_TP(cur)][index or self.get_RP()]

    def set_val(self, value, index=None, cur=True):
        self.MX[self.get_TP(cur)][index or self.get_RP()] = value

    def get_TP(self, cur=True):
        return self.TPS[cur]

    def set_TP(self, tape_num):
        self.TPS.append(tape_num)
        self.TPS.pop(0)

    def get_RP(self):
        return self.RPS[self.get_TP()]

    def set_RP(self, index):
        if index < 0:
            LOG(0, 0, "tape index undershot the tape." % TP_S)
        if index >= TP_S: 
            LOG(0, 0, "tape index exceeded the tape." % TP_S)
        self.RPS[self.get_TP()] = index

    def get_expr_tape(self):
        return self.expr_tape

    def set_expr_tape(self, expr_tape):
        self.expr_tape = expr_tape

    def move(self, diff):
        self.set_RP(self.get_RP() + diff)

    def add_cur_to_other(self, value):
        self.set_val(value + self.get_val(cur=False), cur=False)    #TODO

    def add_other_to_cur(self):
        self.set_val(self.get_val(cur=False) + self.get_val(), cur=True)

    def call(self, ref):
        return ss_eval(self.FT[ref], self)

    def defun(self, ref, expr):
        self.FT[ref] = expr

class ExprTape:

    def __init__(self):
        self.tape = [0, 0, 0, 0, 0, 0, 0, 0]
        self.RP = 0
        #self.structs = []
        #self.expr_tape = ExprTape()

    def get_type(self): return "tape"

    def get_val(self, index=None):
        return self.tape[index or self.RP]

    def set_val(self, value, index=None):
        self.tape[index or self.RP] = value

    def set_RP(self, index):
        if index >= TP_S: LOG(0, 0, "tape index exceeded the tape.")
        elif index < 0: LOG(0, 0, "tape index undershot the tape.")
        self.RP = index

    def get_RP(self):
        return self.RP

    def set_tape(self, tape):
        self.tape = tape

    def get_tape(self):
        return self.tape

    def get_expr_tape(self):
        return self.expr_tape

    def set_expr_tape(self, expr_tape):
        self.expr_tape = expr_tape

    def move(self, diff):
        self.set_RP(self.RP + diff)

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

    def __repr__(self):
        def gen_pos():
            for i, pos in enumerate(self.indexes):
                pos = format(pos, "3d")
                if pos == " -1": pos = "   "
                if i == self.pos: pos = "\x1b[46m%s\x1b[0m" % pos
                yield pos
        return "<{:>2s}@{}>".format(self.byte, "|".join(gen_pos()))
    
    def check_indexes(self):
        return self.indexes[0] < self.indexes[1] < self.indexes[2]

    def has_mid(self):
        return True if self.indexes[1] > -1 else False

    def get_self_index(self):
        return self.indexes[self.pos]

    def get_index(self, pos):
        return self.indexes[self.pos_t[pos]]

    def set_index(self, pos, val):
        if val < 1: LOG(0, 1, "Index too low")
        self.indexes[self.pos_t[pos]] = val

    def get_indexes(self):
        return self.indexes

    def set_indexes(self, indexes):
        if len(indexes) != 3: LOG(0, 2, "Indexes number not match.")
        self.indexes = indexes

    def get_other_end(self):
        if self.pos == 1: LOG(0, 1, "No such method for a `mid' type.")
        return self.indexes[2 - self.pos]

    def set_other_end(self, index):
        if index < 0: LOG(0, 1, "Index too low")
        if self.pos == 1: LOG(0, 1, "No such method for a `mid' type.")
        self.indexes[2 - self.pos] = index

    def matched(self):
        return True if self.get_other_end() else False

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

def test(expr, glob_env):
    """
    bool test(str expr)
    Used to eval the expression in a condition.
    """
    comp = expr[:2]
    expr = expr[2:]
    cur_val = get_val()
    expr_tape = ExprTape()
    parse_expr(expr, expr_tape, glob_env)
    val = expr_tape.get_val()
    
    if comp == "<<": comp = "<"
    elif comp == ">>": comp = ">"
    elif comp == "/=": comp = "!="

    return eval("{:d}{}{:d}".format(cur_val, comp, val))

def struct_scan(expr):
    """
    void struct_scan(str expr)
    Scan the structures of an expression.
    Raises Exceptions upon error.
    """
    structs = [None for i in expr]
    unmatched = []
    IP = 0
    loop = False
    while IP < len(expr):
        byte = expr[IP]
        #print("BYTE::", byte)
        if byte in L_BRAC:
            if byte == "[" and unmatched[-1][1] == "?[" :
                start, struct_t = unmatched[-1]
                structs[IP] = brac_t("?[", "mid", IP)
                structs[start].set_index("mid", IP)
                structs[IP].set_index("start", start)
            else:
                unmatched += [[IP, byte]]
                structs[IP] = brac_t(byte, "start", IP)
            #print("UNMATCHED::", unmatched)
        elif byte in R_BRAC:
            start, struct_t = unmatched.pop()
            structs[IP] = brac_t(struct_t, "end", IP)
            structs[start].set_other_end(IP)
            structs[IP].set_other_end(start)
            if structs[start].has_mid():
                mid = structs[start].get_index("mid")
                structs[mid].set_index("end", IP)
                structs[IP].set_index("mid", mid)
            #print("UNMATCHED::", unmatched, "BYTE::", byte)
        elif byte == '?':
            if expr[IP + 1] not in "!$":
                new_IP = 0
                struct_t = "?"
                if expr[IP + 3] == "(":
                    new_IP = IP + 3
                    level = 0
                    while True:
                        _byte = expr[new_IP]
                        if _byte in L_BRAC: level += 1
                        elif _byte in R_BRAC: level -= 1
                        new_IP += 1
                        if not level: break
                else: new_IP = get_parsable_length(expr[IP + 3:])
                print("IDENTIFIER::", expr[new_IP])
                if expr[new_IP] == "[": struct_t = "?["
                structs[IP] = brac_t(struct_t, "start", IP)
                unmatched += [[IP, struct_t]]
                #print("UNMATCHED::", unmatched)
                IP += 2
            else:
                IP += 1
                if expr[IP] == "!":
                    #print("UNMATCHED::", unmatched)
                    start, struct_t = unmatched[-1]
                    structs[start].set_index("mid", IP)
                    structs[IP] = brac_t('?', "mid", IP)
                    structs[IP].set_index("start", start)
                elif expr[IP] == "$":
                    start, struct_t = unmatched.pop()
                    structs[start].set_index("end", IP)
                    structs[IP] = brac_t('?', "end", IP)
                    structs[IP].set_index("start", start)
                    if structs[start].has_mid():
                        mid = structs[start].get_index("mid")
                        structs[mid].set_index("end", IP)
                        structs[IP].set_index("mid", mid)
                else:
                    LOG(0, 2, "Unrecognized symbol.")
        IP += 1
    return structs

def parse(expr, env, glob_env, structs=None):
    if not structs: structs = struct_scan(expr)
    print("EXPR::", expr, "TYPE::", env.get_type())
    IP = 0
    param = None
    while IP < len(expr):
        new_IP = get_parsable_length(expr[IP:]) + IP
        parsable_expr = expr[IP:new_IP]
        for c in parsable_expr[::-1]:
            if c == "(":
                other_end = structs[new_IP - 1].get_other_end()
                param = parse_expr(expr[new_IP:other_end], env, \
                        glob_env, structs[new_IP:other_end])
                new_IP = other_end
                #print("OTHER_END::", expr[IP])
            elif c == ";": return param or env.get_val()
            else: param = bi_eval(c, param, env, glob_env)
        IP = new_IP

def parse_expr(expr, env, glob_env, structs=None, ret_tape=False):
    expr_tape = ExprTape()
    parse(expr, expr_tape, glob_env, structs)
    glob_env.set_expr_tape(expr_tape)
    if ret_tape: return expr_tape.get_tape()
    return expr_tape.get_val()

def bi_parsable(expr, index):
    diff = 0
    if expr[index] == "?":
        bi_expr = expr[index:index + 4] 
        cond_t1 = re.compile("^\?((>=)|(==)|(<=)|(>>)|(<<)|(/=))[%s]$" % RETN)
        cond_t2 = re.compile("^\?[!$]$")
        if cond_t1.match(bi_expr) or cond_t2.match(bi_expr): diff = 4
    else:
        bi_expr = expr[index:index + 2]
        reci_t = re.compile("[%s%s][%s%s]" % (OPER, RECI, OPER, RETN))
        # Bi-parsing type of oper that receive an param
        oper_t = re.compile("[%s][%s]" % (OPER, OPER))
        # no two successive opers can be parsed
        if reci_t.match(bi_expr) and not oper_t.match(bi_expr): diff = 2
    return diff

def get_parsable_length(expr):
    index = 0
    while index < len(expr):
        diff = bi_parsable(expr, index)
        if diff: index += diff - 1
        else: break
    return index + 1

def bi_eval(oper, param, env, glob_env):
    """
    bi_eval(char oper, int param, Env env, Env glob_env) -> operation/value
    Parse these opers:
    ~ # @ $ % ^ ! * + - < > : ; , . = /
    Bi-parsing is applicable to these opers.
    """
    print("EVALUATED::", oper, param)
    is_oper = False if param == None else True
    if oper in OPER:
        exec("env.set_val(env.get_val() %c %d)" % \
                (oper, param or (1 if oper in "+-" else 2)))
    elif oper == "~":
        if is_oper:
            LOG(3, 0, "Tape number requested: %d" % param)
            if param > 7 or param < 0:
                LOG(0, 0, "Tape number out of range.")
            env.set_TP(param)
        else: return env.get_TP()
    elif oper == "#": 
        if is_oper: env.set_RP(param)
        else: return env.get_RP()
    elif oper == "@": env.add_cur_to_other(param or env.get_val())
    elif oper == "$":
        if is_oper:
            if param == -1: return expr_tape_old
            return env.get_val(param)
        # Expression cell
        return env.get_val()
    elif oper == "!": env.add_other_to_cur()
    elif oper in "<>": env.move((ord(oper) - 61) * param)
    elif oper == ":":
        old_RP = env.get_RP()
        env.set_RP(param or old_RP)
        retn = ss_eval(env.FT[param or env.get_val()])
        env.set_RP(old_RP)
        return retn
    elif oper == ";": return param or env.get_val() #TODO
    elif oper == ",": env.set_val(getchar())
    elif oper == ".": putchar(param or env.get_val())
    elif oper == "=": sys.exit(param or env.get_val())

    return 0
