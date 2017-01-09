#include "list.h"

void free_list(l_list *head) {
    l_list *old, *ptr = malloc(sizeof(l_list));
    while (ptr != NULL) {
        old = ptr;
        ptr = ptr->next;
        free(old);
    }
}

void stack_push(l_list **stack, l_list *list) {
    l_list *ptr = list;
    while (ptr->next != NULL)
        ptr = ptr->next;
    ptr->next = *stack;
    *stack = list;
}

l_list *stack_pop(l_list **stack) {
    l_list *old = *stack;
    *stack = (*stack)->next;
    return old;
}

void stack_pushi(l_list **stack, ss_inst *inst) {
    l_list *data = malloc(sizeof(l_list));
    data->name = inst->type;
    data->index = inst;
    stack_push(stack, data);
    free(data);
}

ss_inst *stack_popi(l_list **stack) {
    l_list *poped = stack_pop(stack);
    ss_inst *inst = poped->index;
    free(poped);
    return inst;
}
