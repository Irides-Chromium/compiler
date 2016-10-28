#!/usr/bin/python3
TP_S = 1024
MX_S = 4

import sys, re
from putchar import putchar
ALL = "-+*/^%<>~`!@#$={[()]},.;:?"
BI_PAR = "~#@$%^!*+-<>:,.=/&`"  # Bi-parsable
OPER = "-+*/^%<>"   # "Operators"
MATH_OP = "-+*/^*"  # Math operators
RETN = "-+~#$:,(`"  # opers that return a value (an expr as well)
A_RETN = "$:,(`"    # Always return a value
EITHER = "-+~#"     # opers that either return a value or receive a value
RECI = "~#$@!:;.="  # opers that receive a value
A_RECI = "$@!:;.="  # Always tries to receive a value
BRAC = "{[()]}"     # The brackets
L_BRAC = "{[("
R_BRAC = ")]}"
#stderr = open("ss_stderr.log", "w")
stderr = sys.stderr         # DEBUG

class Env:

    def __init__(self):

        self.MX = [[0 for i in range(TP_S)] for i in range(MX_S)]
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
        return self.MX[self.get_TP(cur)][index or self.get_RP(cur)]

    def set_val(self, value, index=None, cur=True):
        self.MX[self.get_TP(cur)][index or self.get_RP(cur)] = value

    def get_TP(self, cur=True):             # For ~
        return self.TPS[cur]

    def set_TP(self, tape_num):             # For ~
        self.TPS.append(tape_num % MX_S)
        self.TPS.pop(0)

    def get_RP(self, cur=True):
        return self.RPS[self.get_TP(cur)]

    def set_RP(self, index):
        #if index < 0: LOG(0, 0, "tape index undershot the tape." % TP_S)
        #if index >= TP_S: LOG(0, 0, "tape index exceeded the tape." % TP_S)
        self.RPS[self.get_TP()] = index % TP_S

    def get_expr_tape(self):
        return self.expr_tape

    def set_expr_tape(self, expr_tape):
        self.expr_tape = expr_tape

    def move(self, diff):                   # For <>
        self.set_RP(self.get_RP() + diff)

    def add_cur_to_last(self, value):      # For @
        self.set_val(value + self.get_val(cur=False), cur=False)    #TODO

    def add_last_to_cur(self, value):      # For !
        self.set_val(value + self.get_val())

    def call_by_ind(self, ref, env):
        return parse(expr[self.FT[ref]], env, self, env.structs[self.FT[ref]])

    def defun_by_ind(self, ref, start_ind, end_ind):
        self.FT[ref] = slice(start_ind, end_ind)

    def defun_by_expr(self, ref, expr):     # For {}
        self.FT[ref] = expr

    def call_by_expr(self, ref, env):       # For :
        parse(self.FT[ref], env, self)

class ExprTape:

    def __init__(self):
        self.tape = [0, 0, 0, 0, 0, 0, 0, 0]
        self.RP = 0
        #self.structs = []
        #self.expr_tape = ExprTape()

    def __repr__(self):
        return "tape(%s)" % ", ".join((str(i) for i in self.tape))

    def get_type(self): return "tape"

    def get_val(self, index=None):
        return self.tape[index or self.RP]

    def set_val(self, value, index=None):
        self.tape[index or self.RP] = value

    def set_RP(self, index):
        #if index >= TP_S: LOG(0, 0, "tape index exceeded the tape.")
        #elif index < 0: LOG(0, 0, "tape index undershot the tape.")
        self.RP = index % TP_S

    def get_RP(self):
        return self.RP

    def set_tape(self, tape):
        self.tape = tape

    def get_tape(self):
        return self.tape

    #def get_expr_tape(self):
    #    return self.expr_tape

    #def set_expr_tape(self, expr_tape):
    #    self.expr_tape = expr_tape

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
                pos = "   " if pos == -1 else format(pos, "3d")
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
        if val < 0: LOG(0, 1, "Index too low")
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
    #print("".join((log[log_t], "/[", event[event_t], "]: ", message)), \
    #        file=stderr)
    retn = int(return_val[log_t])
    if retn > 0:
        if stderr != sys.stderr: stderr.close()
        #sys.exit(retn)
        raise Exception
    return retn

def equi(byte1, byte2):
    is_brac = BRAC.index(byte1) + BRAC.index(byte2) == 5
    is_cond = byte1 in "?!$" and byte2 in "?!$"
    return is_brac or is_cond or byte1 == byte2

def test(expr, env, glob_env):
    """
    bool test(str expr)
    Used to eval the expression in a condition.
    Example: ">>(++++)"
    """
    print("TESTING EXPR::", expr)
    comp = expr[:2]
    expr = expr[2:]
    cur_val = env.get_val()
    #print("cur_val::", cur_val)
    #print("VALUE EXPR::", expr[1:-1])
    val = parse_expr(expr[1:-1], env, glob_env)
    #print("test::val::", val)

    if comp == "<<": comp = "<"
    elif comp == ">>": comp = ">"
    elif comp == "/=": comp = "!="

    #print("EVAL EXPR::", "{:d}{}{:d}".format(cur_val, comp, val))
    return eval("{:d}{}{:d}".format(cur_val, comp, val))

def struct_scan(expr):
    """
    void struct_scan(str expr)
    Scan the structures of an expression.
    Raises Exceptions upon error.
    """
    #print("SCANNING EXPR::", expr)
    structs = [None for i in expr]
    unmatched = []
    IP = 0
    loop = False
    while IP < len(expr):
        byte = expr[IP]
        #print("BYTE::", byte)
        if byte in L_BRAC:
            if byte == "[" and len(unmatched) and unmatched[-1][1] == "?[":
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
                struct_t = "?"
                new_IP = IP + 3
                if expr[new_IP] == "(":
                    level = 0
                    while True:
                        _byte = expr[new_IP]
                        if _byte in L_BRAC: level += 1
                        elif _byte in R_BRAC: level -= 1
                        new_IP += 1
                        if not level: break
                    brac_structs = struct_scan(expr[IP + 3:new_IP])
                    for struct in brac_structs:
                        if struct:
                            struct.set_indexes([i+IP+3 if i > -1 else -1 \
                                    for i in struct.get_indexes()])
                    structs[IP + 3:new_IP] = brac_structs
                else: new_IP = get_parsable_length(expr[IP + 3:]) + new_IP
                #print("struct_scan::expr[IP+3:new_IP]::", expr[IP + 3:new_IP])
                #print("IDENTIFIER::", expr[new_IP])
                if expr[new_IP] == "[": struct_t = "?["
                structs[IP] = brac_t(struct_t, "start", IP)
                unmatched += [[IP, struct_t]]
                #print("UNMATCHED::", unmatched)
                IP = new_IP - 1
                #print("LAST CHAR::", expr[IP])
            else:
                if expr[IP + 1] == "!":
                    #print("UNMATCHED::", unmatched)
                    #print("BEFORE Excep::", structs, unmatched)
                    start, struct_t = unmatched[-1]
                    structs[start].set_index("mid", IP)
                    structs[IP] = brac_t('?', "mid", IP)
                    structs[IP].set_index("start", start)
                elif expr[IP + 1] == "$":
                    start, struct_t = unmatched.pop()
                    structs[start].set_index("end", IP)
                    structs[IP] = brac_t('?', "end", IP)
                    structs[IP].set_index("start", start)
                    if structs[start].has_mid():
                        mid = structs[start].get_index("mid")
                        structs[mid].set_index("end", IP)
                        structs[IP].set_index("mid", mid)
                else: LOG(0, 2, "Unrecognized symbol %c." % expr[IP + 1])
                IP += 1
        IP += 1
    return structs

def parse(expr, env, glob_env, structs=None):
    if not structs: structs = struct_scan(expr)
    #print("EXPR::", expr, "TYPE::", env.get_type())
    IP = 0
    while IP < len(expr):
        new_IP = get_parsable_length(expr[IP:]) + IP
        #print("COND SCAN1::", expr[IP:new_IP])
        parsable_expr = expr[IP:new_IP]
        if parsable_expr[0] != "?":
            param = None
            last_ch = parsable_expr[1:][-2:-1]
            if last_ch == "+" or last_ch == "-":
                param = 44 - ord(last_ch)
                parsable_expr = parsable_expr[:-1]
            for c in parsable_expr[::-1]:
                if c in BI_PAR: param = bi_eval(c, param, env, glob_env)
                elif c in L_BRAC:
                    other_end = structs[new_IP - 1].get_other_end()
                    if c == "(":
                        param = parse_expr(expr[new_IP:other_end], env, \
                                glob_env, structs[new_IP:other_end])
                        #print("OTHER_END::", expr[IP])
                    elif c == "[":
                        while env.get_val() != 0:
                            parse_expr(expr[new_IP:other_end], env, \
                                    glob_env, structs[new_IP:other_end])
                    elif c == "{": glob_env.defun_by_expr(env.get_val(), \
                                expr[new_IP:other_end])
                    new_IP = other_end
                elif c == ";": return param or env.get_val()
        else:
            new_IP -= 1
            #print("SCAN EXPR::", expr[new_IP:])
            if expr[new_IP] == "(":
                new_IP = structs[new_IP].get_other_end() + 1
            else: new_IP = get_parsable_length(expr[new_IP:]) + new_IP
            # ?>>$$~
            #print("COND SCAN2::", expr[IP:new_IP])
            struct = structs[IP]
            indexes = [i for i in struct.get_indexes() if i > -1]
            if struct.byte == "?":
                conseq = slice(new_IP, indexes[1])
                alt = slice(0) if len(indexes) == 2 \
                                else slice(indexes[1] + 2, indexes[2])
                expr_slice = conseq \
                        if test(expr[IP + 1:new_IP], env, glob_env) \
                        else alt
                #print("CONSEQ::", conseq, "ALT::", alt)
                parse(expr[expr_slice], env, glob_env, structs[expr_slice])
            elif struct.byte == "?[":
                loop_range = slice(indexes[1] + 1, indexes[2])
                while test(expr[IP + 1:new_IP], env, glob_env):
                    parse(expr[loop_range], env, glob_env, \
                            structs[loop_range])
            new_IP = structs[IP].get_other_end() + 2
        IP = new_IP

def parse_expr(expr, glob_env, structs=None, ret_tape=False):
    expr_tape = ExprTape()
    set_expr = True
    #print("parse_expr::expr::", expr)
    if expr[0] == "!":
        set_expr = False
        expr = expr[1:]
    parse(expr, expr_tape, glob_env, structs)
    if set_expr: glob_env.set_expr_tape(expr_tape)
    if ret_tape: return expr_tape.get_tape()
    return expr_tape.get_val()

def get_parsable_length(expr):
    index = 0
    while index < len(expr):
        #print(expr[index])
        diff = bi_parsable(expr, index)
        if diff: index += diff - 1
        else: break
    match = re.search(".[%s]." % EITHER, expr[:index + 1])
    if match: return match.start() + 2
    return index + 1
    # End the expression immediately after RETNs

def bi_parsable(expr, index):
    bi_expr = expr[index:index + 4]
    if re.match("^\?(>=|==|<=|>>|<<|/=)[%s]$" % RETN, bi_expr): return 4
    bi_expr = expr[index:index + 2]
    if re.match("^\?[!$]$", bi_expr): return 2

    # Bi-parsing type of oper that receive an param
            # no two successive opers can be parsed
    if re.match("[%s%s][%s%s]" % (OPER, RECI, MATH_OP, RETN), bi_expr) \
            and not re.match("[%s][%s]" % (OPER, OPER), bi_expr): return 2

def bi_eval(oper, param, env, glob_env):
    """
    bi_eval(char oper, int param, Env env, Env glob_env) -> operation/value
    Parse these opers:
    ~ # @ $ % ^ ! * + - < > : , . = / & `
    Bi-parsing is applicable to these opers.
    `param` can be None, a value, or a ExprTape.
    """
    #print("EVALUATED::", oper, param)
    has_param = False if param == None else True
    if oper in MATH_OP:
        op = "**" if oper == "^" else oper
        if type(param) != list:
            exec("env.set_val(env.get_val() %s %d)" % \
                (op, param if has_param else (1 if oper in "+-" else 2)))
        elif len(param) == 8:
            env.set_tape_right([eval("i %s v" % op) \
                for i, v in zip(env.get_tape_right(), param)])
    elif oper in "<>": env.move((ord(oper) - 61) * \
            (param if has_param else 1))
    elif oper == "$": return env.get_val(param)
    elif oper == "@": return glob_env.get_val(param)
    elif oper == ".": putchar(param or env.get_val())
    elif oper == ",": env.set_val(ord(sys.stdin.read(1)))
    elif oper == "`": return env.expr_tape.get_val()
    elif oper == "&": return env.expr_tape.get_tape()
    elif oper == "~":
        if has_param:
            LOG(3, 0, "Tape number requested: %d" % param)
            env.set_TP(param)
        else: return env.get_TP()
    #elif oper == "!": env.add_last_to_cur(param or env.get_val(cur=False))
    elif oper == "!": env.add_cur_to_last(param or env.get_val())
    elif oper == "#": return env.set_RP(param)
    elif oper == ":": return glob_env.call_by_expr( \
            param if has_param else env.get_val(), env)
    #elif oper == ";": return param or env.get_val()
    elif oper == "=": sys.exit(param or env.get_val())
    #elif oper == "#":
    #    print("Current tape: %d" % (env.CT + 1))
    #    for tape_num in [0, 1]:
    #        print("Tape number: %d" % (tape_num + 1))
    #        ptr = env.RP[tape_num]
    #        lo = ptr - 5
    #        hi = ptr + 7
    #        for index in range(lo, hi): print("%4d" % (index%TP_S), end='')
    #        print()
    #        for index in range(lo, hi):
    #            print("%5d " % env.RT[tape_num][index % TP_S], \
    #                    end='')
    #        print()
    #        for index in range(lo, hi):
    #            print("    ^ " if index == ptr else "      ", \
    #                    end='')
    #        print()

    return 0
