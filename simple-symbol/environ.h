#ifndef _ENVIRON_H
#   define _ENVIRON_H

#include <string.h>
#include <stdbool.h>
#include "io.h"
#include "list.h"

extern short ENV_TP_S, ENV_MX_S, EXPR_TP_S;
extern char *RETN, *RECI, *OPER, *L_BRAC, *ALL, *BI_PAR, *OPER, *MATH_OP, *RETN, *EITHER, *RECI, *BRAC, *L_BRAC, *R_BRAC;

typedef short index_t;
typedef double value_t;

/* 
 * The special expression cell with a length of 8.
 */

typedef struct {
    char type;
    value_t tape[8];
    index_t RP;
} ExprTape;

/*
 * The main tape for the whole program, with 4 tapes, each with 1024 cells.
 */

typedef struct {
    char type;
    value_t tape[4][1024];
    index_t TPS[2];
    index_t RPS[4];
    l_list *FT;
    l_list *func_ptr;
    ExprTape *expr_tape;
} Env;

/*
 * the parameter type used for bi-parsing. Can be a double sized value or a
 * expression tape. Type is decided by the char-typed `type` variable. Every
 * time the type of the parameter is changed, `type` should also change.
*/

typedef enum {
    PARAM_NULL_TYPE,    /* Null typed parameter (no parameter) */
    PARAM_SING_TYPE,    /* Single value parameter (double typed) */
    PARAM_TAPE_TYPE     /* Tape parameter */
} param_val_type_t;

typedef struct {
    union {
        ExprTape *tape;
        value_t val;
    } value;
    param_val_type_t type;
} param_t;

void append_func(l_list *head, value_t ref, ss_inst *ind);
void redef_func(l_list *head, value_t ref, ss_inst *ind);
ss_inst *find_func(l_list *head, value_t ref);

Env *init_env();
ExprTape *init_expr();
void destroy_expr(ExprTape *expr_tape);
void destroy_env(Env *env);

index_t get_RP(void *self, bool cur);
index_t get_TP(void *self, bool cur);
value_t get_val(void *self);
value_t get_val_index(void *self, index_t index);
value_t get_val_last(void *self);
ExprTape *get_tape_right(void *self);
void set_RP(void *self, bool cur, index_t index);
void set_TP(void *self, bool cur, index_t value);
void set_val(void *self, value_t value);
void set_val_index(void *self, index_t index, value_t value);
void set_val_last(void *self, value_t value);
void add_cur_to_last(void *self, value_t value);
void move(void *self, int diff);
void env_set_expr_tape(Env *self, ExprTape *expr_tape);
void set_tape_right(void *self, ExprTape *tape);
void env_defunc(Env *self, value_t ref, ss_inst *ind);
value_t env_call(Env *glob_env, value_t ref);
ExprTape *env_get_expr_tape(Env *self);
value_t *expr_get_tape(ExprTape *self);

#endif /* _ENVIRON_H */
