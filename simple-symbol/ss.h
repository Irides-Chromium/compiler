//#ifndef SS_H
//#   define SS_H

#include <math.h>
#include <sys/types.h>
#include <time.h>

#include "parse.h"

#define list_op(op, l1, l2, res)  \
    for (int i = 0; i < 8; i++) \
        res[i] = l1[i] op l2[i];

value_t parse(char *expr, char *end, void *env, Env *glob_env);
param_t parse_expr(char *expr, Env *glob_env);
bool test(char *expr, Env *env, Env *glob_env);

param_t wrap_null();
param_t wrap_tape(ExprTape *expr_tape);
param_t wrap_value(value_t value);
param_t bi_eval(char oper, param_t param, void *env, Env *glob_env);

void print_first(void *self, Env *glob);

void LOG(err_level lvl, char *fmt, ...);

//#endif /* SS_H */
