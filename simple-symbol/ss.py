#!/usr/bin/python3

import sys, re, random
from putchar import putchar
ALL = "-+*/^%<>~`!@#$={[()]},.;:?_\""
BI_PAR = "~#@$%^!*+-<>:,.=/&`_"  # Bi-parsable
OPER = "-+*/^%<>"   # "Operators"
MATH_OP = "-+*/^%"  # Math operators
RETN = "~@#$:(`&"  # opers that return a value (an expr as well)
EITHER = "~#"       # opers that either return a value or receive a value
RECI = "~#$@!:;.="  # opers that receive a value
BRAC = "{[()]}"     # The brackets
L_BRAC = "{[("
R_BRAC = ")]}"
#stderr = open("ss_stderr.log", "w")
stderr = sys.stderr         # DEBUG

class Env:
    TP_S = 1024
    MX_S = 4

    def __init__(self):

        self.MX = [[0 for i in range(self.TP_S)] for i in range(self.MX_S)]
        # Array for tapes
        self.TPS = [0, 0]                # Tape Pointer Stack
        #           ^ |^
        #old tape     |new tape (current)
        self.RPS = [0, 0, 0, 0] # Register Pointer Stack
        self.expr_tape = ExprTape()
        self.FT = {}            # Function Reference
        #self.structs = []

    def get_val(self, cur=True, index=None):
        #print("INDEX REQ::", index)
        index = choice(self.get_RP(cur), index) % self.TP_S
        #print("ACTUAL INDEX::", index)
        return self.MX[self.get_TP(cur)][index]

    def set_val(self, value, cur=True, index=None):
        index = choice(self.get_RP(cur), index) % self.TP_S
        self.MX[self.get_TP(cur)][index] = value

    def get_mem(self, index=None):
        index = choice(self.get_RP() + self.get_TP() * self.TP_S, index)
        return self.MX[index // self.TP_S][index % self.TP_S]

    def get_TP(self, cur=True):             # For ~
        return self.TPS[cur]

    def set_TP(self, tape_num):             # For ~
        if tape_num == -1: tape_num = self.get_TP(False)
        self.TPS.append(tape_num % self.MX_S)
        self.TPS.pop(0)

    def get_RP(self, cur=True):
        return self.RPS[self.get_TP(cur)]

    def set_RP(self, index):
        #if index < 0: LOG(0, 0, "tape index undershot the tape." % TP_S)
        #if index >= TP_S: LOG(0, 0, "tape index exceeded the tape." % TP_S)
        self.RPS[self.get_TP()] = index % self.TP_S

    def get_expr_tape(self):
        return self.expr_tape

    def set_expr_tape(self, expr_tape):
        self.expr_tape = expr_tape

    def get_tape_right(self, index=None):
        start = choice(self.get_RP(), index)
        return [self.get_val(index=i) for i in range(start, start + 8)]

    def set_tape_right(self, tape, index=None):
        start = choice(self.get_RP(), index)
        for i in range(start, start + 8): self.set_val(tape[i], index=i) 

    def move(self, diff):                   # For <>
        self.set_RP(self.get_RP() + diff)

    def add_cur_to_last(self, value):      # For !
        self.set_val(value + self.get_val(False), False)    #TODO

    def defunc(self, ref, expr):     # For {}
        self.FT[ref] = expr

    def call(self, ref, env):       # For :
        #print("FUNC REF::", ref)
        parse(self.FT[ref], env, self)

class ExprTape:
    TP_S = 8

    def __init__(self):
        self.tape = [0, 0, 0, 0, 0, 0, 0, 0]
        self.RP = 0

    def __repr__(self):
        return "tape%s" % str(tuple(self.tape))

    def get_type(self): return self.__class__.__name__

    def get_val(self, index=None):
        #print("DEBUG::index::", index or self.RP)
        return self.tape[index or self.RP]

    def set_val(self, value, index=None):
        self.tape[index or self.RP] = value

    def set_RP(self, index):
        #if index >= TP_S: LOG(0, 0, "tape index exceeded the tape.")
        #elif index < 0: LOG(0, 0, "tape index undershot the tape.")
        self.RP = index % self.TP_S

    def get_RP(self):
        return self.RP

    #def set_tape(self, tape):
    def get_RP(self):
        return self.RP

    #def set_tape(self, tape):
    #    self.tape = tape

    def get_tape(self):
        return self.tape

    def move(self, diff):
        self.set_RP(self.RP + diff)

class brac_t:
    """
    Use for matchable structures: ()[]{}\" and ?...?!?$
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

    def has_mid(self):
        return self.indexes[1] > -1

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

def LOG(log_t, event_t, message):
    log = "FWDIV"
    # Fatal, Warning, Debug, Info, Verbose
    return_val = "32000"
    event = ["MEM Management", "Brackets", "Expression"]
    print(log[log_t], "/[", event[event_t], "]: ", message, sep="", \
            file=stderr)
    retn = int(return_val[log_t])
    if retn > 0:
        if stderr != sys.stderr: stderr.close()
        #sys.exit(retn)
        raise Exception
    return retn

def choice(val1, val2, cond=None):
    return val1 if val2 == cond else val2

def test(expr, env, glob_env):
    """
    bool test(str expr)
    Used to eval the expression in a condition.
    Example: ">>(++++)"
    """
    #print("TESTING EXPR::", expr)
    comp = expr[:2]
    expr = expr[2:]
    cur_val = env.get_val()
    #print("cur_val::", cur_val)
    #print("VALUE EXPR::", expr[1:-1])
    #print("OUT OF parse_expr::", expr)
    val = parse_expr("!" + (expr[1:-1] if expr[0:1] == "(" \
            else expr), env, glob_env)
    #print("test::val::", val)

    if comp == "<<": comp = "<"
    elif comp == ">>": comp = ">"
    elif comp == "/=": comp = "!="

    #print("EVAL EXPR::", "{:d}{}{:d}".format(cur_val, comp, val))
    return eval("%d%s%d" % (cur_val, comp, val))

def trans_structs(structs, diff):       #TODO Change to diff mode
    "Shift the indexes in a struct to fit deeper parse."
    for struct in structs:
        if struct: struct.set_indexes([i + diff if i > -1 else -1 \
                    for i in struct.get_indexes()])
    return structs

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
        #print("UNMATCHED::", unmatched)
        if byte in L_BRAC:
            #if len(unmatched): print("BUG::", structs[unmatched[-1][0]])
            if byte == "[" and len(unmatched) \
                    and unmatched[-1][1] == "?[" \
                    and not structs[unmatched[-1][0]].has_mid():
                start, struct_t = unmatched[-1]
                structs[IP] = brac_t("?[", "mid", IP)
                structs[start].set_index("mid", IP)
                structs[IP].set_index("start", start)
            else:
                unmatched.append([IP, byte])
                structs[IP] = brac_t(byte, "start", IP)
        elif byte in R_BRAC:
            start, struct_t = unmatched.pop()
            structs[IP] = brac_t(struct_t, "end", IP)
            structs[start].set_other_end(IP)
            structs[IP].set_other_end(start)
            if structs[start].has_mid():
                mid = structs[start].get_index("mid")
                structs[mid].set_index("end", IP)
                structs[IP].set_index("mid", mid)
        elif byte == '?':
            if expr[IP + 1] not in "!$":
                struct_t = "?"
                new_IP = get_parsable_length(expr[IP:]) + IP
                #print("AFTER GET::", expr[IP:new_IP])
                if expr[new_IP - 1] == "(":
                    count = 1
                    while True:
                        _byte = expr[new_IP]
                        if _byte in L_BRAC: count += 1
                        elif _byte in R_BRAC: count -= 1
                        new_IP += 1
                        if not count: break
                    structs[IP + 3:new_IP] = trans_structs( \
                            struct_scan(expr[IP + 3:new_IP]), IP + 3)
                elif expr[new_IP - 1] in RETN:
                    new_IP += get_parsable_length(expr[new_IP + 1:])
                #print("struct_scan::expr[IP+3:new_IP]::", expr[IP + 3:new_IP])
                #print("IDENTIFIER::", expr[new_IP])
                if expr[new_IP] == "[": struct_t = "?["
                structs[IP] = brac_t(struct_t, "start", IP)
                unmatched.append([IP, struct_t])
                IP = new_IP - 1
                #print("LAST CHAR::", expr[IP])
            else:
                if expr[IP + 1] == "!":
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
                else: LOG(0, 2, "Unrecognized symbol: %c." % expr[IP + 1])
                IP += 1
        elif byte == "\"":
            end = 0
            quote = expr.find("\"", IP + 1)
            newline = expr.find("\n", IP + 1)
            if quote == -1:
                if newline == -1: raise Exception("Comment not ended.")
                else: end = newline
            elif quote < newline: end = quote
            else: end = newline
            #print("REST::", IP, end, expr[IP:])
            structs[IP] = brac_t("\"", "start", IP)
            structs[end] = brac_t("\"", "end", end)
            structs[IP].set_other_end(end)
            structs[end].set_other_end(IP)
            IP = end
        IP += 1
    return structs

def parse(expr, env, glob_env, structs=None):
    structs = struct_scan(expr)
    #print("PARSING EXPR::", expr)
    IP = 0
    while IP < len(expr):
        new_IP = get_parsable_length(expr[IP:]) + IP
        #print("parsable_expr::", expr[IP:new_IP])
        parsable_expr = expr[IP:new_IP]
        if parsable_expr[0] != "?":
            param = None
            for c in parsable_expr[::-1]:
                if c in BI_PAR: param = bi_eval(c, param, env, glob_env)
                elif c in L_BRAC + "\"":
                    other_end = structs[new_IP - 1].get_other_end()
                    s = slice(new_IP, other_end)
                    if c == "(":
                        #print("OTHER_END::", other_end)
                        param = parse_expr(expr[s], glob_env)
                        #print("param::", param)
                        #print("OTHER_END::", expr[IP])
                    elif c == "[":
                        while env.get_val() != 0:
                            #print("VALUE::", env.get_val())
                            parse(expr[s], env, glob_env)
                    elif c == "{": glob_env.defunc(env.get_val(), expr[s])
                    elif c == "\"": other_end += 1
                    new_IP = other_end
                elif c == ";": return choice(env.get_val(), param)
        else:
            new_IP -= 1
            #print("SCAN EXPR::", expr[new_IP:])
            if expr[new_IP] == "(":
                new_IP = structs[new_IP].get_other_end() + 1
            else: new_IP = get_parsable_length(expr[new_IP:]) + new_IP
            #print("DEBUG::", expr[IP:new_IP])
            struct = structs[IP]
            indexes = [i for i in struct.get_indexes() if i > -1]
            #print("STRUCTS::", structs)
            #print("INDEXES::", indexes)
            #print("EXPR::", expr)
            #print("IP, new_IP::", expr[IP:new_IP])
            if struct.byte == "?":
                conseq = slice(new_IP, indexes[1])
                alt = slice(0) if len(indexes) == 2 \
                                else slice(indexes[1] + 2, indexes[2])
                #print("SLICES::", expr[conseq], expr[alt])
                expr_slice = conseq \
                        if test(expr[IP + 1:new_IP], env, glob_env) \
                        else alt
                #print("CONSEQ::", expr[conseq], "ALT::", expr[alt], "(%s)" % expr)
                #print("SLICE::", expr[expr_slice])
                parse(expr[expr_slice], env, glob_env)
                new_IP = structs[IP].get_other_end() + 1
            elif struct.byte == "?[":
                loop_range = slice(indexes[1] + 1, indexes[2])
                while test(expr[IP + 1:new_IP], env, glob_env):
                    parse(expr[loop_range], env, glob_env)
                new_IP = structs[IP].get_other_end()
            #print("LAST::", expr[new_IP:])
        IP = new_IP

def parse_expr(expr, glob_env, structs=None):
    expr_tape = ExprTape()
    set_expr = True
    ret_tape = False
    #print("parse_expr::expr::", expr)
    flags = re.match("[|!]*", expr).group(0)
    if "!" in flags: set_expr = False
    if "|" in flags: ret_tape = True
    expr = expr[len(flags):]
    #print("AFTER FLAGS::", expr)
    retn = parse(expr, expr_tape, glob_env, structs)
    if set_expr: glob_env.set_expr_tape(expr_tape)
    if ret_tape: return expr_tape.get_tape()
    return expr_tape.get_val()# if retn == None else retn

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
    if re.match("\?(>=|==|<=|>>|<<|/=)[%s]" % RETN, bi_expr): return 4
    elif re.match("\?(>=|==|<=|>>|<<|/=).", bi_expr): return 3
    bi_expr = expr[index:index + 2]
    if re.match("\?[!$]", bi_expr): return 2

    # Bi-parsing type of oper that receive an param
            # no two successive opers can be parsed
    if re.match("[%s][%s]" % (OPER + RECI, RETN), bi_expr) \
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
        elif len(param) == 8: env.set_tape_right([eval("i %s v" % op) \
                            for i, v in zip(env.get_tape_right(), param)])
    elif oper in "<>": env.move((ord(oper) - 61) * \
            (param if has_param else 1))
    elif oper == "$": return env.get_val(index=param)
    elif oper == "@": return glob_env.get_val(index=param)
    elif oper == "_": return 0
    elif oper == ".": putchar(param or env.get_val())
    elif oper == ",": env.set_val(ord(sys.stdin.read(1)))
    elif oper == "`": return glob_env.expr_tape.get_val()
    elif oper == "|": return glob_env.expr_tape.get_tape()
    elif oper == "&": return random.randint(0, 65535)
    elif oper == "~":
        if has_param:
            LOG(3, 0, "Tape number requested: %d" % param)
            env.set_TP(param)
        else: return env.get_TP()
    #elif oper == "!": env.add_last_to_cur(param or env.get_val(cur=False))
    elif oper == "!": env.add_cur_to_last(param or env.get_val())
    elif oper == "#":
        if has_param: env.set_RP(param)
        else: return env.get_RP()
    elif oper == "\\": env.set_val(int(env.get_val()))
    elif oper == ":":
        #print("HAS PARAM::", has_param)
        #print("IN bi_eval::", param if has_param else env.get_val())
        return glob_env.call(param if has_param else env.get_val(), env)
    #elif oper == ";": return param or env.get_val()
    elif oper == "=": sys.exit(param if has_param else env.get_val())
    #elif oper == "#":
    #    #print("Current tape: %d" % (env.CT + 1))
    #    for tape_num in [0, 1]:
    #        #print("Tape number: %d" % (tape_num + 1))
    #        ptr = env.RP[tape_num]
    #        lo = ptr - 5
    #        hi = ptr + 7
    #        for index in range(lo, hi): #print("%4d" % (index%TP_S), end='')
    #        #print()
    #        for index in range(lo, hi):
    #            #print("%5d " % env.RT[tape_num][index % TP_S], \
    #                    end='')
    #        #print()
    #        for index in range(lo, hi):
    #            #print("    ^ " if index == ptr else "      ", \
    #                    end='')
#"""Simple Symbol - a brainfuck like programming language by Steven Zhu.
#Usage: %s [-i | --intera] [-h | --help] [-f | --file file] [-s | --source source]
#Options:
#    -i, --intera    Enter interactive mode.
#    -h, --help      Show this help message and exit.
#    -f, --file      Run a specified file.
#    -s, --source    Source the file before running.
#When no option is supplied, the program will read code from stdin.""")
#    sys.exit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--intera", help="Enter interactive mode.", 
            action="store_true")
    parser.add_argument("-s", "--source", help="Source the file.",
            action="append")
    parser.add_argument("-f", "--file", help="Run the file.")
    parser.add_argument("-c", "--code", help="Run the code.")
    args = parser.parse_args()
    env = Env()
    if args.source:
        for file in args.source: parse(open(file).read(), env, env)
    if args.intera:
        print("Simple Symbol 1.0.0 by Steven Zhu")
        while True:
            try: parse(input(">>> ") + "\n", env, env)
            except EOFError: sys.exit(print("\nBye!"))
            except KeyboardInterrupt: print()
    if args.code: parse(args.code, env, env)
    else:
        try: parse(sys.stdin.read(), env, env)
        except KeyboardInterrupt: sys.exit(print())
