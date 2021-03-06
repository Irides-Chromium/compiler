#include "parse.h"

ss_inst *init_inst(char type, char *expr) {
    ss_inst *self = malloc(sizeof(ss_inst));
    self->type = type;
    self->expr = expr;

    int branch_no;
    switch (type) {
        case '?': branch_no = 4; break;
        case 'w': branch_no = 3; break;
        case '[':
        case '{':
        case '(': branch_no = 2; break;
        default: branch_no = 1; break;
    }
    self->branch_no = branch_no;
    self->indexes = calloc(branch_no, sizeof(ss_inst *));
    return self;
}

ss_inst *parse_until(stream_t *stream, char until) {
    char start;
    switch (until) {
        case ')': start = '('; break;
        case ']': start = '['; break;
        case '}': start = '{'; break;
    }
    int count = 1;
    long IP, new_IP;
    new_IP = IP = getpos(stream);
    while (count) {
        char ch = getch(stream);
        if (ch == start) count++;
        else if (ch == until) count--;
    }
    new_IP = getpos(stream);
    int len = new_IP - IP - 1;
    char *buf = calloc(len + 1, sizeof(char));
    setpos(stream, IP);
    getstr(stream, len, buf);
    setpos(stream, new_IP);
    stream_t *sub_stream = init_stream('s', buf);
    ss_inst *expr = init_insts(sub_stream);  /* {expr} */
    close_stream(sub_stream);
    free(buf);
    return expr;
}

ss_inst *init_insts(stream_t *stream) {
    char *buf;
    char type;
    long IP, new_IP;
    new_IP = IP = getpos(stream);
    ss_inst *head, *ptr;
    ss_inst *indexes[4];
    head = ptr = malloc(sizeof(ss_inst));
    while (listench(stream)) {
        int len = get_parsable_length(stream);
        buf = calloc(len + 1, sizeof(char));
        getstr(stream, len, buf);
        if (buf[len - 1] == '(' && *buf == '?') {
            type = '(';
            indexes[1] = parse_until(stream, ')');
        } else if (*buf == '[') {
            type = '[';
            indexes[1] = parse_until(stream, ']');
        } else if (*buf == '{') {
            type = '{';
            indexes[1] = parse_until(stream, '}');
        } else if (*buf == '?') {
            type = '?';
            char iden = buf[len - 1];
            if (iden == '(') {
                indexes[1] = parse_until(stream, ')');/* {expr} */
            } else if (strchr(RETN, iden)) {
                move_stream(stream, 1);
                new_IP += get_parsable_length(stream);
                move_stream(stream, -1);
            }
            if (listench(stream) == '[') type = 'w';
            move_stream(stream, new_IP - IP - 1);
            // TODO conseq & alt and loop body
        } else {
            type = 0;
        }
        indexes[0] = init_inst(type, buf);
        if (type) {
            for (int i = 1; i < indexes[0]->branch_no; i ++)
                indexes[0]->indexes[i] = indexes[i];
            move_stream(stream, new_IP - IP - 1);
        }
        ptr->indexes[0] = indexes[0];
        ptr = ptr->indexes[0];
    }
    ss_inst *retn = head->indexes[0];
    free_inst(head);
    return retn;
}

void free_inst(ss_inst *obj) {
    free(obj->expr);
    free(obj->indexes);
    free(obj);
}

void free_insts(ss_inst *obj) {
    for (int i = 0; i < obj->branch_no; i ++)
        if (obj->indexes[i])
            free_insts(obj->indexes[i]);
    free_inst(obj);
}

bool inst_has_mid(ss_inst *self) {
    return self->indexes[POS_MID] != NULL;
}

ss_inst *inst_get_index(ss_inst *self, pos_t pos) {
    return self->indexes[pos];
}

void inst_set_index(ss_inst *self, pos_t pos, ss_inst *index) {
    self->indexes[pos] = index;
}

ss_inst **inst_get_indexes(ss_inst *self) {
    return self->indexes;
}

void inst_set_indexes(ss_inst *self, ss_inst **indexes) {
    memcpy(self->indexes, indexes, 24);
}

//ss_inst *inst_get_other_end(ss_inst *self) {
//    return self->indexes[2 - self->pos];
//}

//void inst_set_other_end(ss_inst *self, ss_inst *index) {
//    self->indexes[2 - self->pos] = index;
//}

/* bi_parsable:
 * @param char *expr: the pointer of the Instruction Pointer
 * @return: length of parsable instructions
 */

int bi_parsable(stream_t *stream) {
    char expr[8] = "";
    getstr(stream, 4, expr);
    LOG(INFO, "bipars::expr:: %s", expr);
    move_stream(stream, -4);
    regex_t *pattern = malloc(sizeof(regex_t));
    int len = 0;
    /* Conditional start                     |  RETNs   |*/
    regcomp(pattern, "^\\?(>=|==|<=|>>|<<|/=)[~@#$:(`|_&]", 1);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 4;
        goto end;
    }

    regfree(pattern);
    /* Conditional start simplified */
    regcomp(pattern, "^\\?(>=|==|<=|>>|<<|/=).", 1);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 3;
        goto end;
    }

    regfree(pattern);
    /* Conditional else or end */
    regcomp(pattern, "^\\?[!$]", 1);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 2;
        goto end;
    }

    regfree(pattern);
    /* RECI & RETN */
    /*                 | OPER  ||  RECI  ||   RETN   | */
    regcomp(pattern, "^[-+*/^%<>~#$@!:;.=][~@#$:(`|_&]", 1);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        regfree(pattern);
        /* NOT two operators */
        /*                 |  OPER  ||  OPER  | */
        regcomp(pattern, "^[-+*/^%<>][-+*/^%<>]", 1);
        if (regexec(pattern, expr, 0, 0, 0))
            len = 2;
    }

end:
    regfree(pattern);
    free(pattern);
    move_stream(stream, len);
    LOG(INFO, "bipars::len:: %d", len);
    return len;
}

/* get_parsable_length:
 * @param char *expr: the pointer of the Instruction Pointer
 * @return: the maximum parsable length
 */

int get_parsable_length(stream_t *stream) {
    long IP, new_IP;
    new_IP = IP = getpos(stream);
    int diff;
    LOG(DEBUG, "next:: %u", listench(stream));
    while (listench(stream)) {
        diff = bi_parsable(stream);
        if (diff) {
            LOG(DEBUG, "inloop:: %d", diff);
        } else break;
    }
    new_IP = getpos(stream);
    int len = new_IP - IP - 1;
    char *buf = calloc(len + 1, sizeof(char));

    setpos(stream, IP);
    getstr(stream, len, buf);
    setpos(stream, new_IP);
    int pars_len;
    regmatch_t *match = malloc(sizeof(regmatch_t));
    regex_t *pattern = malloc(sizeof(regex_t));
    regcomp(pattern, ".[~#].", 0);

    if (!regexec(pattern, buf, 1, match, 0))
        pars_len = match->rm_so + 2;
    else
        pars_len = len;
    regfree(pattern);
    free(pattern);
    free(match);
    return pars_len;
}
