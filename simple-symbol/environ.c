#include "environ.h"

char *ALL = "-+*/^%<>~`|!@#$={[()]},.;:?\"";
char *BI_PAR = "~#@$%^!*+-<>:,.=/&`|_";  // Bi-parsable
char *OPER = "-+*/^%<>";   // "Operators"
char *MATH_OP = "-+*/^%";  // Math operators
char *RETN = "~@#$:(`|_&";  // opers that return a value (an expr as well)
char *EITHER = "~#";     // opers that either return a value or receive a value
char *RECI = "~#$@!:;.=";  // opers that receive a value
char *BRAC = "{[()]}";     // The instkets
char *L_BRAC = "{[(";
char *R_BRAC = ")]}";
short ENV_TP_S = 1024;
short ENV_MX_S = 4;
short EXPR_TP_S = 8;

void append_func(l_list *tail, value_t ref, ss_inst *ind) {
    tail->next = malloc(sizeof(l_list));
    tail = tail->next;
    tail->name = ref;
    tail->index = ind;
    tail->next = NULL;
}

void redef_func(l_list *head, value_t ref, ss_inst *ind) {
    while (head) {
        if (head->name == ref)
            break;
        head = head->next;
    }
    head->index = ind;
}

ss_inst *find_func(l_list *head, value_t ref) {
    while (head) {
        if (head->name == ref)
            return head->index;
        head = head->next;
    }
    return NULL;
}

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
    self->func_ptr = self->FT = malloc(sizeof(l_list));
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
        LOG(ERROR, "There is no tape number for an {expr}.");
    return 0;
}

void set_TP(void *self, bool cur, index_t value) {
    if (*((char *) self) == 'g')
        ((Env *) self)->TPS[cur] = value;
    else
        LOG(ERROR, "There is no tape number for an {expr}.");
}

index_t get_RP(void *self, bool cur) {
    if (*((char *) self) == 'x')
        return ((ExprTape *) self)->RP;
    else if (*((char *) self) == 'g')
        return ((Env *) self)->RPS[get_TP(self, true)];
    return 0;
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
    return 0;
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
    return 0;
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
        LOG(ERROR, "Cannot get the last tape number for an {expr}.");
    return 0;
}

void set_val_last(void *self, value_t value) {
    if (*((char *) self) == 'g')
        ((Env *) self)->tape[get_TP(self, false)]
            [get_RP(self, false)] = value;
    else
        LOG(ERROR, "Cannot get the last tape number for an {expr}.");
}

void add_cur_to_last(void *self, value_t value) {
    if (*((char *) self) == 'g')
        set_val_last(self, value + get_val_last(self));
    else
        LOG(ERROR, "Cannot get the last tape number for an {expr}.");
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

void env_defunc(Env *self, value_t ref, ss_inst *ind) {
    l_list *func_ptr = self->func_ptr;
    func_ptr->next = malloc(sizeof(l_list));
    func_ptr = func_ptr->next;
    func_ptr->name = (int) ref;
    func_ptr->index = ind;
    func_ptr->next = NULL;
    self->func_ptr = func_ptr;
}

value_t env_call(Env *glob_env, value_t ref) {
    return 0;
}
