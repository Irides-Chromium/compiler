#include "ssm.h"

static short max_arrptr[4] = {0, 0, 0, 0};

static ssm_obj *read_symbol(stream_t *stream) {
    long pos = getpos(stream);
    char c = listench(stream);
    while (isalnum(c) || strchr("~!@#$%^&*-_=+:/?<>", c))
        c = getch(stream);
    long len = getpos(stream) - pos - 1;
    char *buf = calloc(len + 1, sizeof(char));
    setpos(stream, pos);
    getstr(stream, len, buf);
    ssm_obj *retn = calloc(1, sizeof(ssm_obj));
    retn->type = SYMBOL_T;
    retn->name = buf;
    //PRINTSTR(buf);
    return retn;
    //return intern(root, buf);
}

static ssm_obj *read_number(stream_t *stream) {
    long start = getpos(stream);
    bool flt = false;
    if (listench(stream) == '-')
        getch(stream);

    char c;
    while (true) {
        c = getch(stream);
        if (strchr("1234567890", c))
            continue;
        else if (c == '.') {
            if (flt)
                break;
            flt = true;
        } else
            break;
    }

    move_stream(stream, -1);
    long end = getpos(stream);
    char *buf = calloc(end - start + 1, sizeof(char));
    setpos(stream, start);
    getstr(stream, end - start, buf);

    ssm_obj *result = calloc(1, sizeof(ssm_obj));
    result->type = NUM_T;
    result->val = flt ? atof(buf) : (double) atol(buf);
    free(buf);
    return result;
}

static ssm_obj *read_quote(stream_t *stream) {
    ssm_obj *quote;// = sfind_var(env, "quote");
    ssm_obj *expr = read_expr(stream);
    quote->next = expr;
    return quote;
}

static ssm_obj *read_expr(stream_t *stream) {
    char c;
    while (true) {
        c = listench(stream);
        //LOG(INFO, "    read_expr");
        //PRINTCHAR(c);
        if (c == ' ' || c == '\n' || c == '\r' || c == '\t') {
            getch(stream);
            continue;
        }
        if (c == EOF || c == 0)
            return NULL;
        if (c == ';') {
            while (true) {
                char c = getch(stream);
                if (c == EOF || c == '\n')
                    break;
            }
            continue;
        }
        if (c == '(') {
            getch(stream);
            return read_list(stream);
        }
        if (c == ')') {
            getch(stream);
            return CPAREN;
        }
        if (c == '.') {
            getch(stream);
            return DOT;
        }
        if (c == '\'') {
            getch(stream);
            return read_quote(stream);
        }
        if (strchr("-1234567890", c))
            return read_number(stream);
        if (isalpha(c) || strchr("~!@#$%^&*-_=+:/?<>", c))
            return read_symbol(stream);
        LOG(ERROR, "Invalid character <%c>.", c);
    }
}

static ssm_obj *read_list(stream_t *stream) {
    //LOG(INFO, "read_list");
    read_recur_count++;
    ssm_obj *list = calloc(1, sizeof(ssm_obj));
    ssm_obj *ptr = NULL, *new;
    list->type = LIST_T;
    while (true) {
        new = read_expr(stream);
        print_sslist(new);
        if (!new)
            LOG(ERROR, "Unclosed parenthesis.");
        if (new == CPAREN) {
            read_recur_count--;
            if (list->list)
                return list;
            else {
                free(list);
                return NIL;
            }
        }
        if (new == DOT) {
            ssm_obj *last = read_expr(stream);
            if (read_expr(stream) != CPAREN)
                LOG(ERROR, "Closed parenthesis expected after dot");
            ptr->next = last;
            read_recur_count--;
            return list;
        }
        //*head = cons(root, obj, head);
        if (ptr) {
            ptr->next = new;
            ptr = new;
        } else {
            ptr = new;
            list->list = ptr;
        }
    }
}

void free_obj(ssm_obj *head) {
    switch (head->type) {
        case TRUE_T: case NIL_T: case DOT_T: case CPAREN_T:
            return;
        case BUILTIN_T:
            return;
        case SYMBOL_T:
            free(head->name);
            break;
        case NUM_T:
        case INT_T: case INT_ARR_T:
        case CHAR_T: case CHAR_ARR_T:
        case DOUBLE_T: case DOUBLE_ARR_T:
            break;
        case ENV_T: case LIST_T:
            free_obj(head->list);
            break;
        case FUNC_T: case MACRO_T:
            free_obj(head->param);
            free_obj(head->body);
            break;
    }
    if (head->next) free_obj(head->next);
    free(head);
}

void free_objs(ssm_obj *head) {
    if (head->type == LIST_T)
        free_objs(head->list);
    if (head->next)
        free_objs(head->next);
    free_obj(head);
}

// ==============================================
// Environments
// ==============================================

ssm_obj *init_ssm_env() {
    ssm_obj *env = calloc(1, sizeof(ssm_obj));
    env->type = ENV_T;
    return env;
}

index_t reserve_mem(index_t size, bool sys) {
    int tape_no = sys * 2;
    // Check memory of first tape
    if (ENV_MX_S - 1 - max_arrptr[tape_no] < size)
        tape_no++;
    // Check memory of second tape
    if (ENV_MX_S - 1 - max_arrptr[tape_no] < size)
        LOG(ERROR, "Out of memory");
    index_t ptr = max_arrptr[tape_no] + 1;
    max_arrptr[tape_no] += size;
    return ptr;
}

void add_env(ssm_obj **env) {
    ssm_obj *newenv = calloc(1, sizeof(ssm_obj));
    newenv->type = ENV_T;
    newenv->next = *env;
    *env = newenv;
}

void add_var(ssm_obj *env, ssm_obj *var) {
    ssm_obj *next = env->list;
    var->next = next;
    env->list = var;
}

ssm_obj *sfind_var(ssm_obj *env, char *name) {
    while (env) {
        ssm_obj *var = env->list;
        while (var) {
            if (strcmp(name, var->name) == 0)
                return var;
            var = var->next;
        }
        env = env->next;
    }
    return NULL;
}

// Equivalent to `find' in minilisp. Probably useless
ssm_obj *rfind_var(ssm_obj *env, ssm_obj *ref) {
    while (env) {
        ssm_obj *var = env->list;
        while (var) {
            if (var == ref)
                return var;
            var = var->next;
        }
        env = env->next;
    }
    return NULL;
}

void spit_insts(tape, char *insts);

ssm_obj *eval(ssm_obj *obj, ssm_obj *env) {
    switch (obj->type) {
    case CHAR_T: case INT_T: case DOUBLE_T:
    case CHAR_ARR_T: case INT_ARR_T: case DOUBLE_ARR_T:
    case BUILTIN_T:
    case FUNC_T:
    case TRUE_T:
    case NIL_T:
        // Self-evaluating objects
        return obj;
    case SYMBOL_T: {
        // Variable
        ssm_obj *var = sfind_var(env, obj->name);
        if (var == NULL)
            LOG(ERROR, "Undefined variable: %s", var->name);
        free_obj(obj);
        return var;
    }
    case LIST_T: {
        // Function application form
        if (obj->type != LIST_T)
            LOG(ERROR, "Function application must be a list.");
        ssm_obj *func = obj->list;
        ssm_obj *args = obj->list->next;

        if (func->type != FUNC_T)
            LOG(ERROR, "First member of the list is not a function: %s",
                    func->name);
        //*expanded = macroexpand(root, env, obj);
        //if (*expanded != *obj)
        //    return eval(root, env, expanded);
        //*fn = (*obj)->car;
        //*fn = eval(root, env, fn);
        //*args = (*obj)->cdr;
        //if ((*fn)->type != BUILTIN_T && (*fn)->type != TFUNCTION)
        //    error("The head of a list must be a function");
        return apply(func, args, env);
    }
    default:
        LOG(ERROR, "Unknown type: %d", obj->type);
    }
}

/* 
 * === Builtin Functions ===
 */

// (init <type> <name>)
ssm_builtin_func(init) {
    ssm_obj *type = args->list;
    ssm_obj *var = type->next;
    var->type = NUM_T;
    if (type->type != SYMBOL_T)
        LOG(ERROR, "First argument for `init' is not of type SYMBOL");
    if (strncmp(type->name, "int", 3) == 0) var->type = INT_T;
    else if (strncmp(type->name, "char", 4) == 0) var->type = CHAR_T;
    else if (strncmp(type->name, "double", 6) == 0) var->type = DOUBLE_T;
    else LOG(ERROR, "Unknown type.");
    //Variable addressing
    var->ind = reserve_mem(1, true);

    char *brac_start = strchr(type->name, '[');
    char *brac_end = strchr(type->name, ']');
    if (brac_start && brac_end && \
            brac_end - type->name == strlen(type->name)) {
        ssm_obj *region = calloc(1, sizeof(ssm_obj));
        region->type = var->type + 3;
        if (brac_end - brac_start == 1) {
            region->size = 1;
            LOG(WARNING, "No digit in []. Assuming size is 1.");
        } else {
            char *endptr;
            region->size = strtol(brac_start + 1, &endptr, 10);
            if (endptr != brac_end) {
                if (*endptr == '.')
                    LOG(WARNING, "Truncating float to integer for size.");
                else
                    LOG(ERROR, "Invalid size specifier.");
            }
        }
        //TODO Create region variable
        region->ind = reserve_mem(region->size, true);
    }
}

// (setv name value)
ssm_builtin_func(setv) {
    ssm_obj *name = args->list;
    ssm_obj *var = sfind_var(env, name->name);
    if (var == NULL)
        LOG(ERROR, "Variable `%s' not defined.", name->name);
    ssm_obj *value;// = eval(name->next);
    //TODO Manipulate tape
    free_obj(name);
    free_obj(value);
    return value;
}

// (if cond conseq alt)
ssm_builtin_func(if) {
    ssm_obj *cond;// = eval(args->list);
    ssm_obj *conseq = cond->next;
    ssm_obj *alt = conseq->next;
    ssm_obj *result = cond != NIL ? conseq : alt;
    return result;//eval(result);
}

//(loop cond body)
ssm_builtin_func(loop) {
    ssm_obj *cond;// = eval(args->list);
    ssm_obj *body = cond->next;
    while (cond/*eval(cond)*/ != NIL) {
        //eval(body);
    }
    return NIL;
}

//(at index type)
//(mem index type)
//(set index type value)
//(+ val1 val2)
//(- val1 val2)
//(* val1 val2)
//(/ val1 val2)
//(% val1 val2)
//(^ val1 val2)
//(defun name arglist body)
//(defun ref arglist body)
//(call name arglist)
//(call ref arglist)
//(read len)
//(read-char)
//(write var)
//(write-char char)
//(write-str string)
//(tonum value)
//(random)
//(return value)
//(last-expr)
//(last-val)
//(exit value)
//(add-to-last-tape value)

void print_sslist(ssm_obj *item) {
    for (int i = 0; i < read_recur_count - 1; i ++)
        printf("    ");
    switch (item->type) {
        case NUM_T:
            printf("Number: %f\n", item->val); break;
        case NIL_T:
            printf("NIL\n"); break;
        case TRUE_T:
            printf("TRUE\n"); break;
        case SYMBOL_T:
            printf("Symbol: %s\n", item->name); break;
        case FUNC_T:
            printf("Function: %s\n", item->name); break;
        case MACRO_T:
            printf("Macro: %s\n", item->name); break;
        case LIST_T:
            printf("LIST\n");
            break;
        case DOT_T:
            printf("DOT\n"); break;
        case CPAREN_T:
            printf("CPAREN\n"); break;
    }
    for (int i = 0; i < read_recur_count - 1; i ++)
        printf("    ");
    PRINTPTR(item);
    for (int i = 0; i < read_recur_count - 1; i ++)
        printf("    ");
    puts("--------");
}

void print_slist(ssm_obj *item) {
    print_recur_count++;
    while (item) {
        for (int i = 0; i < print_recur_count - 1; i ++)
            printf("    ");
        switch (item->type) {
            case NUM_T:
                printf("Number: %f\n", item->val); break;
            case NIL_T:
                printf("NIL\n"); break;
            case TRUE_T:
                printf("TRUE\n"); break;
            case SYMBOL_T:
                printf("Symbol: %s\n", item->name); break;
            case FUNC_T:
                printf("Function: %s\n", item->name); break;
            case MACRO_T:
                printf("Macro: %s\n", item->name); break;
            case LIST_T:
                printf("LIST\n");
                break;
            case DOT_T:
                printf("DOT\n"); break;
            case CPAREN_T:
                printf("CPAREN\n"); break;
        }
        for (int i = 0; i < print_recur_count - 1; i ++)
            printf("    ");
        PRINTPTR(item);
        puts("--------");
        if (item->type == LIST_T)
            print_slist(item->list);
        item = item->next;
    }
    print_recur_count--;
}

int main() {
    char *buf = calloc(1024, sizeof(char));
    printf("\e[1;31m%s", ">>> ");
    fgets(buf, 1024, stdin);
    printf("\e[0m");
    //buf[strlen(buf) - 1] = 0;
    stream_t *stream = init_stream('s', buf);

    ssm_obj *list = read_expr(stream);
    puts("\n---------------------------------------------------\n");
    //PRINTINT(list->type);
    //PRINTLONG((long) list->list);
    PRINTPTR(list);
    if (list) {
        PRINTPTR(list->list);
        print_slist(list);
        free_obj(list);
    }
    //printf("%f\n", read_number(stream)->val);
    //ssm_obj *list = read_list(stream);
    //ssm_obj *ptr = list->list;
    //while (ptr) {
    //    printf("<%s>\n", ptr->name);
    //    ptr = ptr->next;
    //}
    //free_obj(list->list);
    //free(list);

    close_stream(stream);
    free(buf);
    return 0;
}

int ssm_main(int argc, char **argv) {
    ssm_obj *env = init_ssm_env();
    //def_builtins(env);
    //eval();
    return 0;
}
