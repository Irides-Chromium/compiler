#include <ctype.h>

#include "ss.h"

#define PRINTINT(var) printf("\e[32mINT\e[0m %s::%d\n", #var, var);
#define PRINTCHAR(var) printf("\e[33mCHAR\e[0m %s::%d <%c>\n", #var, var, var);
#define PRINTLONG(var) printf("\e[34mLONG\e[0m %s::%ld\n", #var, var);
#define PRINTPTR(var) printf("\e[35mPTR\e[0m %s::%p\n", #var, var);
#define PRINTSTR(var) printf("\e[36mSTR\e[0m %s::%s\n", #var, var);

typedef enum {
    NIL_T, 
    TRUE_T, 
    NUM_T,
    SYMBOL_T,
    FUNC_T,
    MACRO_T,
    LIST_T,

    DOT_T,
    CPAREN_T,
    BUILTIN_T,
    ENV_T,

    CHAR_T,
    INT_T,
    DOUBLE_T,
    CHAR_ARR_T,
    INT_ARR_T,
    DOUBLE_ARR_T
} ssm_type;

typedef struct _ssm_obj {
    ssm_type type;
    union {
        // Value for numbers
        double val;
        // Variable/Symbol name
        char *name;
        // Memory locations and sizes for ss tape
        struct {
            index_t ind;
            index_t size;
        };
        // Builtin functions
        struct _ssm_obj *(*func)(struct _ssm_obj *args, struct _ssm_obj *env);
        // Lists (con cells)
        struct _ssm_obj *list;
        // Defined functions
        struct {
            index_t ref;
            struct _ssm_obj *param;
            struct _ssm_obj *body;
            struct _ssm_obj *env;
        };
    };
    struct _ssm_obj *next;
} ssm_obj;

#define ssm_builtin_func(name) ssm_obj *ssm_##name(ssm_obj *args, ssm_obj *env)

static int print_recur_count = 0;
static int read_recur_count = 0;

static ssm_obj *T = &(ssm_obj) {TRUE_T};
static ssm_obj *NIL = &(ssm_obj) {NIL_T};
static ssm_obj *DOT = &(ssm_obj) {DOT_T};
static ssm_obj *CPAREN = &(ssm_obj) {CPAREN_T};

static ssm_obj *read_symbol(stream_t *stream);
static ssm_obj *read_number(stream_t *stream);
static ssm_obj *read_quote(stream_t *stream);
static ssm_obj *read_expr(stream_t *stream);
static ssm_obj *read_list(stream_t *stream);
void print_slist(ssm_obj *);
void print_sslist(ssm_obj *);

void free_objs(ssm_obj *head);
ssm_obj *init_ssm_env();
void add_env(ssm_obj **env);
void add_var(ssm_obj *env, ssm_obj *var);
ssm_obj *sfind_var(ssm_obj *env, char *name);
ssm_obj *rfind_var(ssm_obj *env, ssm_obj *ref);
