#include <stdio.h>
#include <malloc.h>
#include <math.h>
#include <stdbool.h>
#include <ctype.h>

#include "io.h"

#define PRINTINT(var) printf("\e[32mINT\e[0m %s::%d\n", #var, var);
#define PRINTCHAR(var) printf("\e[33mCHAR\e[0m %s::%d <%c>\n", #var, var, var);
#define PRINTLONG(var) printf("\e[34mLONG\e[0m %s::%ld\n", #var, var);
#define PRINTPTR(var) printf("\e[35mPTR\e[0m %s::%p\n", #var, var);
#define PRINTSTR(var) printf("\e[36mSTR\e[0m %s::%s\n", #var, var);

static int print_recur_count = 0;
static int read_recur_count = 0;

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
    PRIMITIVE_T,
    ENV_T
} ssm_type;

typedef struct _ssm_obj {
    ssm_type type;
    union {
        double val;
        char *name;
        struct _ssm_obj *list;
        struct {
            struct _ssm_obj *param;
            struct _ssm_obj *body;
            struct _ssm_obj *env;
        };
    };
    struct _ssm_obj *next;
} ssm_obj;

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

ssm_obj *s_split(stream_t *stream) {
    long space_pos;
    int word_len;
    bool last = false;
    ssm_obj *list = malloc(sizeof(ssm_obj));
    list->type = LIST_T;
    ssm_obj *head = malloc(sizeof(ssm_obj));
    ssm_obj *ptr = head;
    list->list = head;
    while (listench(stream)) {
        space_pos = findch(stream, ' ');
        if (space_pos == -1) {
            last = true;
            space_pos = (long) stream->end;
        }
        word_len = space_pos - getpos(stream);
        if (word_len == 0) {
            move_stream(stream, 1);
            continue;
        } else {
            ptr->name = calloc(word_len + 1, sizeof(char));
            getstr(stream, word_len, ptr->name);
            setpos(stream, space_pos + 1);
        }
        move_stream(stream, 1);
        if (listench(stream) != ' ' && !last) {
            ptr->next = malloc(sizeof(ssm_obj));
            ptr = ptr->next;
            ptr->next = NULL;
        }
        move_stream(stream, -1);
    }
    return list;
}

void free_objs(ssm_obj *head) {
    if (head->type == LIST_T)
        free_objs(head->list);
    if (head->next)
        free_objs(head->next);
    if (head->type == SYMBOL_T)
        free(head->name);
    if (head != T && head != NIL && head != DOT && head != CPAREN)
        free(head);
}

static ssm_obj *intern(char *name) {
    //TODO Find name in env
    ssm_obj *obj = malloc(sizeof(ssm_obj));
    obj->type = SYMBOL_T;
    obj->name = name;
    return obj;
}

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
    ssm_obj *quote = intern("quote");
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
        if (c == EOF)
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
    print_slist(list);
    free_objs(list);
    //printf("%f\n", read_number(stream)->val);
    //ssm_obj *list = read_list(stream);
    //ssm_obj *ptr = list->list;
    //while (ptr) {
    //    printf("<%s>\n", ptr->name);
    //    ptr = ptr->next;
    //}
    //free_objs(list->list);
    //free(list);

    close_stream(stream);
    free(buf);
    return 0;
}
