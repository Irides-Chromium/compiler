#ifndef _LIST_H
#   define _LIST_H

#include <malloc.h>

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
    char type;
    char *expr;
    /*
     * branch_no: the number of pointers to the next instruction.
     * no == 1 (default):
     *      [0] -> next
     * no == 2 (L_BRAC):
     *      [1] -> {expr} (without BRAC)
     * no == 3 (loop):
     *      [1] -> testing expr (`?.*` without `?')
     *      [2] -> {expr} (without BRAC)
     * no == 4 (conditional):
     *      [1] -> testing expr (`?.*` without `?')
     *      [2] -> conseq
     *      [3] -> alternative
     */
    short branch_no;
    struct _ss_inst **indexes;
} ss_inst;

typedef struct _l_list {
    struct _l_list *next;
    int name;
    ss_inst *index;
} l_list;

void free_list(l_list *head);
void stack_push(l_list **stack, l_list *list);
l_list *stack_pop(l_list **stack);
void stack_pushi(l_list **stack, ss_inst *inst);
ss_inst *stack_popi(l_list **stack);

#endif /* _LIST_H */
