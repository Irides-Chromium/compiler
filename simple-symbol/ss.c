#include "ss.h"
//TODO ID env type from ``test.c''
char *ALL = "-+*/^%<>~`!@#$={[()]},.;:?\"";
char *BI_PAR = "~#@$%^!*+-<>:,.=/&`_";  // Bi-parsable
char *OPER = "-+*/^%<>";   // "Operators"
char *MATH_OP = "-+*/^%";  // Math operators
char *RETN = "~@#$:(`_&";  // opers that return a value (an expr as well)
char *EITHER = "-+~#";     // opers that either return a value or receive a value
char *RECI = "~#$@!:;.=";  // opers that receive a value
char *BRAC = "{[()]}";     // The instkets
char *L_BRAC = "{[(";
char *R_BRAC = ")]}";
short ENV_TP_S = 1024;
short ENV_MX_S = 4;
short EXPR_TP_S = 8;

/* Initializations & Deletions */
ExprTape *init_expr() {
    ExprTape *self = malloc(sizeof(ExprTape));
    memset(self->tape, 0, sizeof(int) * 8);
    self->type = 'x';
    self->RP = 0;
    return self;
}

void destroy_expr(ExprTape *expr_tape) {
    free(expr_tape);
}

Env *init_env() {
    Env *self = malloc(sizeof(Env));
    memset(self->tape, 0, sizeof(int) * 4096);
    memset(self->TPS, 0, sizeof(int) * 2);
    memset(self->RPS, 0, sizeof(int) * 4);
    self->type = 'g';
    self->FT = malloc(sizeof(l_list));
    self->func_ptr = self->FT;
    self->expr_tape = init_expr();
    return self;
}

void destroy_env(Env *env) {
    free(env->expr_tape);
    free(env);
}

/* Env & ExprTape methods */

index_t get_TP(void *self, bool cur) {
    if (*((char *) self) == 'g')
        return ((Env *) self)->TPS[cur];
    else
        LOG(true, "There is no tape number for an {expr}.");
}

void set_TP(void *self, bool cur, index_t value) {
    if (*((char *) self) == 'g')
        ((Env *) self)->TPS[cur] = value;
    else
        LOG(true, "There is no tape number for an {expr}.");
}

index_t get_RP(void *self, bool cur) {
    if (*((char *) self) == 'x')
        return ((ExprTape *) self)->RP;
    else if (*((char *) self) == 'g')
        return ((Env *) self)->RPS[get_TP(self, true)];
}

void set_RP(void *self, bool cur, index_t index) {
    if (*((char *) self) == 'x')
        ((ExprTape *) self)->RP = index;
    else if (*((char *) self) == 'g')
        ((Env *) self)->RPS[get_TP(self, true)] = index;
}

value_t get_val(void *self) {
    index_t index = get_RP(self, true);
    if (*((char *) self) == 'x')
        return ((ExprTape *) self)->tape[index];
    else if (*((char *) self) == 'g')
        return ((Env *) self)->tape[get_TP(self, true)][index];
}

void set_val(void *self, value_t value) {
    index_t index = get_RP(self, true);
    if (*((char *) self) == 'x')
        ((ExprTape *) self)->tape[index] = value;
    else if (*((char *) self) == 'g')
        ((Env *) self)->tape[get_TP(self, true)][index] = value;
}

value_t get_val_index(void *self, index_t index) {
    index %= ENV_TP_S;
    if (*((char *) self) == 'x')
        return ((ExprTape *) self)->tape[index % EXPR_TP_S];
    else if (*((char *) self) == 'g')
        return ((Env *) self)->tape[get_TP(self, true)][index % ENV_TP_S];
}

void set_val_index(void *self, index_t index, value_t value) {
    if (*((char *) self) == 'x')
        ((ExprTape *) self)->tape[index % EXPR_TP_S] = value;
    else if (*((char *) self) == 'g')
        ((Env *) self)->tape[get_TP(self, true)][index % ENV_TP_S] = value;
}

value_t get_val_last(void *self) {
    if (*((char *) self) == 'g')
        return ((Env *) self)->tape[get_TP(self, false)]
            [get_RP(self, false)];
    else
        LOG(true, "Cannot get the last tape number for an {expr}.");
}

void set_val_last(void *self, value_t value) {
    if (*((char *) self) == 'g')
        ((Env *) self)->tape[get_TP(self, false)]
            [get_RP(self, false)] = value;
    else
        LOG(true, "Cannot get the last tape number for an {expr}.");
}

void add_cur_to_last(void *self, value_t value) {
    if (*((char *) self) == 'g')
        set_val_last(self, value + get_val_last(self));
    else
        LOG(true, "Cannot get the last tape number for an {expr}.");
}

void move(void *self, int diff) {
    set_RP(self, true, get_RP(self, true) + diff);
}

ExprTape *get_tape_right(void *self) {
    index_t start = get_RP(self, true);
    ExprTape *tape = malloc(sizeof(ExprTape));
    for (int i=0;i<8;i++) tape->tape[i] = get_val_index(self, start + i);
    return tape;
}

void set_tape_right(void *self, ExprTape *tape) {
    index_t start = get_RP(self, true);
    for (int i=0;i<8;i++) set_val_index(self, start + i, tape->tape[i]);
}

/* ExprTape methods */

value_t *expr_get_tape(ExprTape *self) {
    return self->tape;
}

/* Env methods */

ExprTape *env_get_expr_tape(Env *self) {
    return self->expr_tape;
}

void env_set_expr_tape(Env *self, ExprTape *expr_tape) {
    self->expr_tape = expr_tape;
}

// TODO env_defunc && env_call

void env_defunc(Env *self, value_t ref, index_t ind) {
    l_list *func_ptr = self->func_ptr;
    func_ptr->next = malloc(sizeof(l_list));
    func_ptr = func_ptr->next;
    func_ptr->name = ref;
    func_ptr->index = ind;
    func_ptr->next = NULL;
    self->func_ptr = func_ptr;
}

value_t env_call(Env *glob_env, value_t ref) {
    return 0;
}

/* param_t methods */

param_t wrap_null() {
    union param_val_t param_val;
    param_val.val = 0;
    param_t param = {param_val, PARAM_NULL_TYPE};
    return param;
}

param_t wrap_tape(ExprTape *expr_tape) {
    union param_val_t param_val;
    param_val.tape = expr_tape;
    param_t param = {param_val, PARAM_TAPE_TYPE};
    return param;
}

param_t wrap_value(value_t value) {
    union param_val_t param_val;
    param_val.val = value;
    param_t param = {param_val, PARAM_SING_TYPE};
    return param;
}

/* ss_inst methods */

ss_inst *init_inst(char byte, pos_t pos) {
    ss_inst *self = malloc(sizeof(ss_inst));
    self->byte = byte;
    self->pos = pos;
    memset(self->indexes, 0, 24);
    return self;
}

//void print_inst(ss_inst *self) {
//    printf("<%c@", self->byte);
//    for (int i = 0; i < 3; i ++) {
//        char pos[4];
//        if (self->indexes[i] == NULL)
//            sprintf(pos, "   ");
//        else
//            sprintf(pos, "%3d", self->indexes[i]);
//
//        printf(i == self->pos ? "\x1b[46m%s\x1b[0m" : "%s", pos);
//
//        if (i < 2)
//            printf("|");
//    }
//    printf("\n");
//}

bool inst_has_mid(ss_inst *self) {
    return self->indexes[POS_MID] != NULL;
}

ss_inst *inst_get_index(ss_inst *self, pos_t pos) {
    return self->indexes[pos];
}

void inst_set_index(ss_inst *self, pos_t pos, ss_inst *index) {
    self->indexes[pos] = index;
}

ss_inst **inst_get_indexes(ss_inst *self) {
    return self->indexes;
}

void inst_set_indexes(ss_inst *self, ss_inst **indexes) {
    memcpy(self->indexes, indexes, 24);
}

ss_inst *inst_get_other_end(ss_inst *self) {
    return self->indexes[2 - self->pos];
}

void inst_set_other_end(ss_inst *self, ss_inst *index) {
    self->indexes[2 - self->pos] = index;
}

/* parse:
 * Parse an expression in an environment.
 * @param char *expr: the expression to be parsed
 * @param char *end: the end of the expression
 * @param void *env: the environment to operate on
 * @param Env *glob_env: the global environment
 * @return: the value returned by `;` if there is any
 */

value_t parse(char *expr, char *end, void *env, Env *glob_env) {
    return 0;
}

/* parse_expr:
 * Parse an expression explicitly in an expression tape.
 * @param char *expr: the expression to be parsed
 * @param Env *glob_env: the global env to set the tape
 * @return: the param to return
 */

param_t parse_expr(char *expr, Env *glob_env) {
    ExprTape *expr_tape = init_expr();
    bool set_expr = true;
    bool ret_tape = false;
    regmatch_t *match;
    regex_t *pattern = malloc(sizeof(regex_t));
    regcomp(pattern, "^[|!]*", 0);
    regexec(pattern, expr, 1, match, 0);
    for (int i = match->rm_so; i < match->rm_eo; i ++) {
        switch (*(expr + i)) {
            case '!': set_expr = false; break;
            case '|': ret_tape = true; break;
            default: break;
        }
    }
    expr += match->rm_eo - match->rm_so;
    parse(expr, NULL, expr_tape, glob_env);
    if (set_expr) env_set_expr_tape(glob_env, expr_tape);
    if (ret_tape) return wrap_tape(expr_tape);
    return wrap_value(get_val(expr_tape));
}

/* test: test the bool value of an expression. Used in Conditionals.
 * @param expr: the WHOLE expression to be tested, including comparison
 * string.
 * @param env, glob_env: Environmen and global environment.
 */

bool test(char *expr, Env *env, Env *glob_env) {
    int comp = expr[0] + expr[1];
    int cur_val = get_val(env);
    expr += 2;
    int val = parse_expr(expr + 1, glob_env).value.val;

    switch (comp) {
        case 108: return cur_val != val;
        case 120: return cur_val  < val;
        case 121: return cur_val <= val;
        case 122: return cur_val == val;
        case 123: return cur_val >= val;
        case 124: return cur_val  > val;
        default: LOG(false, 
                "Unrecognized comparison. Returning false.");
    }
    return false;
}

/* get_parsable_length:
 * @param char *expr: the pointer of the Instruction Pointer
 * @return: the maximum parsable length
 */

char *get_parsable_length(char *IP) {
    char *old_IP = IP;
    while (*IP) {
        int diff = bi_parsable(IP);
        if (diff) IP += diff - 1;
        else break;
    }

    char buf[32];
    snprintf(buf, IP - old_IP, "%s", IP);
    regmatch_t *match;
    regex_t *pattern = malloc(sizeof(regex_t));
    regcomp(pattern, ".[~#].", 0);
    if (!regexec(pattern, buf, 1, match, 0))
        return old_IP + match->rm_so + 2;
    return IP + 1;
}

/* bi_parsable:
 * @param char *expr: the pointer of the Instruction Pointer
 * @return: length of parsable instructions
 */

int bi_parsable(char *expr) {
    regex_t *pattern = malloc(sizeof(regex_t));
    int cflags = REG_EXTENDED;
    char buf[64];
    int len = 1;
    sprintf(buf, "^\\?(>=|==|<=|>>|<<|/=)[%s]", RETN);
    /* Conditional start */
    regcomp(pattern, buf, cflags);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 4;
        goto end;
    }

    regfree(pattern);
    /* Conditional start simplified */
    regcomp(pattern, "^\\?(>=|==|<=|>>|<<|/=).", cflags);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 3;
        goto end;
    }

    regfree(pattern);
    /* Conditional else or end */
    regcomp(pattern, "^\\?[!$]", cflags);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 2;
        goto end;
    }

    regfree(pattern);
    /* RECI & RETN */
    sprintf(buf, "^[%s%s][%s]", OPER, RECI, RETN);
    regcomp(pattern, buf, cflags);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        regfree(pattern);
        /* NOT two operators */
        sprintf(buf, "^[%s][%s]", OPER, OPER);
        regcomp(pattern, buf, cflags);
        if (regexec(pattern, expr, 0, 0, 0))
            len = 2;
    }

end:
    regfree(pattern);
    free(pattern);
    return len;
}

/*
 * bi_eval(char oper, int param, Env env, Env glob_env) -> operation/value
 * Parse these opers:
 * ~ # @ $ % ^ ! * + - < > : , . = / & `
 * Bi-parsing is applicable to these opers.
 * `param` can be None, a value, or a ExprTape.
 */

param_t bi_eval(char oper, param_t param, void *env, Env *glob_env) {
    bool has_param = param.type != PARAM_NULL_TYPE;
    value_t cell_val = get_val(env);
    if (param.type != PARAM_TAPE_TYPE) {
        value_t param_val = param.value.val;
        switch (oper) {
            case '+':
                set_val(env, cell_val + has_param ? param_val : 1);
                break;
            case '-':
                set_val(env, cell_val - has_param ? param_val : 1);
                break;
            case '*':
                set_val(env, cell_val * has_param ? param_val : 2);
                break;
            case '/':
                set_val(env, cell_val / has_param ? param_val : 2);
                break;
            case '%':
                set_val(env,fmod(cell_val, has_param ? param_val : 2));
                break;
            case '^':
                set_val(env, pow(cell_val, has_param ? param_val : 2));
                break;
            case '<':
                move(env, - has_param ? param_val : 1);
                break;
            case '>':
                move(env, has_param ? param_val : 1);
                break;
            case '$':
                return wrap_value(get_val_index(env, 
                            has_param ? param_val : -1));
            case '@':
                return wrap_value(get_val_index(glob_env,
                            has_param ? param_val : -1));
            case '_':
                return wrap_value(0);
            case '.':
                putchar(has_param ? param_val : cell_val);
                break;
            case ',':
                set_val(env, getchar());
                break;
            case '`':
                return wrap_value(get_val(glob_env->expr_tape));
            case '|':
                return wrap_tape(glob_env->expr_tape);
            case '&':
                srandom(time(NULL));
                return wrap_value(random() % 65536);
            case '~':
                if (has_param) {
                    char *log_msg;
                    sprintf(log_msg, "Tape number requested: %f",
                            param_val); 
                    LOG(false, log_msg);
                    set_TP(env, true, param_val);
                    break;
                } else {
                    return wrap_value(get_TP(env, true));
                }
            case '!':
                add_cur_to_last(env, has_param ? param_val : get_val(env));
                break;
            case '#':
                if (has_param) {
                    set_RP(env, true, param_val);
                    break;
                } else {
                    return wrap_value(get_RP(env, true));
                }
            case '\\':
                set_val(env, (int) get_val(env));
                break;
            case ':':
                //printf("HAS PARAM::%d\n", has_param)
                //printf("IN bi_eval::%d\n", has_param ? param_val : get_val(env));
                return wrap_value(env_call(glob_env, 
                            has_param ? param_val : get_val(env)));
            case '=':
                    exit(has_param ? param_val : get_val(env));
        }
    } else {
        value_t *expr_tape = param.value.tape->tape;
        value_t *tape_right = get_tape_right(env)->tape;
        ExprTape *result = init_expr();
        switch (oper) {
            case '+':
                list_op(+, tape_right, expr_tape, result->tape);
                break;
            case '-':
                list_op(-, tape_right, expr_tape, result->tape);
                break;
            case '*':
                list_op(*, tape_right, expr_tape, result->tape);
                break;
            case '/':
                list_op(/, tape_right, expr_tape, result->tape);
                break;
            case '%':
                for (int i = 0; i < 8; i ++)
                    result->tape[i] = fmod(tape_right[i], expr_tape[i]);
                break;
            case '^':
                for (int i = 0; i < 8; i ++)
                    result->tape[i] = pow(tape_right[i], expr_tape[i]);
                break;
        }
        set_tape_right(env, result);
    }
}

//int main (int argc, char **argv) {
//    Env *env = init_env();
//    ExprTape expr_tape = init_expr();
//    return EXIT_SUCCESS;
//}
