#include <math.h>
#include <regex.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <stdarg.h>

#define LOG(stat, msg) fprintf(stderr, "%s\n", msg); if (stat) exit(stat);
#define list_op(op, l1, l2, res)  \
    for (int i = 0; i < 8; i++) \
        res[i] = l1[i] op l2[i];

typedef short index_t;
typedef double value_t;

typedef struct _l_list {
    struct _l_list *next;
    value_t name;
    index_t index;
} l_list;

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
    union param_val_t {
        ExprTape *tape;
        value_t val;
    } value;
    param_val_type_t type;
} param_t;

/*
 * Use for matchable structures: ()[]{}`` and ?...?!?$, ?[].
 * `byte` denotes the type of the structure, which can be `(`, `[`, `{`,
 * `?`, `?[`.
 * `pos` denotes the actual relative position of the structure, which can
 * be 0 (start), 1 (mid), or 2 (end).
 * `indexes` denotes the actual indexes of the structure.
 */

typedef enum {
    POS_START,
    POS_MID,
    POS_END
} pos_t;

typedef struct _ss_inst {
    char byte;
    pos_t pos;
    struct _ss_inst *indexes[3];
} ss_inst;

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
void env_defunc(Env *self, value_t ref, index_t ind);
value_t env_call(Env *glob_env, value_t ref);
ExprTape *env_get_expr_tape(Env *self);
value_t *expr_get_tape(ExprTape *self);

ss_inst *init_inst(char byte, pos_t pos);
bool inst_has_mid(ss_inst *self);
ss_inst *inst_get_index(ss_inst *self, pos_t pos);
ss_inst **inst_get_indexes(ss_inst *self);
ss_inst *inst_get_other_end(ss_inst *self);
void inst_set_index(ss_inst *self, pos_t pos, ss_inst *index);
void inst_set_indexes(ss_inst *self, ss_inst **indexes);
void inst_set_other_end(ss_inst *self, ss_inst *index);

int bi_parsable(char *expr);
char *get_parsable_length(char *IP);
value_t parse(char *expr, char *end, void *env, Env *glob_env);
param_t parse_expr(char *expr, Env *glob_env);
bool test(char *expr, Env *env, Env *glob_env);

param_t wrap_null();
param_t wrap_tape(ExprTape *expr_tape);
param_t wrap_value(value_t value);
param_t bi_eval(char oper, param_t param, void *env, Env *glob_env);

void print_inst(ss_inst *self);
void print_first(void *self, Env *glob);
