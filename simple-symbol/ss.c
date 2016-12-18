#include "ss.h"

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
    regmatch_t *match = malloc(sizeof(regmatch_t));
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
        default: LOG(WARNING, 
                "Unrecognized comparison. Returning false.");
    }
    return false;
}

/* param_t methods */

param_t wrap_null() {
    param_t param;
    param.type = PARAM_NULL_TYPE;
    param.value.val = 0;
    return param;
}

param_t wrap_tape(ExprTape *expr_tape) {
    param_t param;
    param.type = PARAM_TAPE_TYPE;
    param.value.tape = expr_tape;
    return param;
}

param_t wrap_value(value_t value) {
    param_t param;
    param.type = PARAM_SING_TYPE;
    param.value.val = value;
    return param;
}

/* ss_inst methods */

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
                    LOG(false, "Tape number requested: %d", param_val);
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
    return wrap_null();
}

int main (int argc, char **argv) {
    Env *env = init_env();
    ExprTape expr_tape = init_expr();
    return EXIT_SUCCESS;
}
