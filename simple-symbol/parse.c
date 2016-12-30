#include "parse.h"

ss_inst *init_inst(char type, char *expr) {
    ss_inst *self = malloc(sizeof(ss_inst));
    self->type = type;
    strncpy(self->expr, expr, 16);

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
    self->indexes = malloc(branch_no * sizeof(ss_inst *));
    return self;
}

ss_inst *parse_until(stream_t *IP, char until) {
    char start;
    switch (until) {
        case ')': start = '('; break;
        case ']': start = '['; break;
        case '}': start = '{'; break;
    }
    int count = 1;
    stream_t *new_IP = malloc(sizeof(stream_t));
    *new_IP = *IP;
    while (count) {
        char ch = getch(new_IP);
        if (ch == start) count++;
        else if (ch == until) count--;
    }
    int diff = get_diff(IP, new_IP) - 1;
    stream_t *sub_stream = malloc(sizeof(stream_t));
    sub_stream->stream.str = malloc(diff * sizeof(char));
    getstr(new_IP, diff, sub_stream->stream.str);
    free(new_IP);
    return init_insts(sub_stream);  /* {expr} */
}

ss_inst *init_insts(stream_t *IP) {
    char *buf;
    char type;
    ss_inst *head, *ptr;
    stream_t *new_IP = malloc(sizeof(stream_t));
    *new_IP = *IP;
    head = ptr = malloc(sizeof(ss_inst));
    l_list *stack = malloc(sizeof(l_list));
    while (listench(IP)) {
        buf = malloc(16 * sizeof(char));
        ss_inst **indexes = malloc(4 * sizeof(ss_inst *));
        getstr(new_IP, get_parsable_length(new_IP), buf);
        if (buf[strlen(buf) - 1] == '(' && *buf == '?') {
            type = '(';
            indexes[1] = parse_until(IP, ')');
        } else if (*buf == '[') {
            type = '[';
            indexes[1] = parse_until(IP, ']');
        } else if (*buf == '{') {
            type = '{';
            indexes[1] = parse_until(IP, '}');
        } else if (*buf == '?') {
            type = '?';
            char iden = buf[strlen(buf) - 1];
            if (iden == '(') {
                indexes[1] = parse_until(IP, ')');  /* {expr} */
            } else if (strchr(RETN, iden)) {
                move_stream(new_IP, 1);
                new_IP += get_parsable_length(new_IP);
                move_stream(new_IP, -1);
            }
            if (listench(new_IP) == '[') type = 'w';
            move_stream(IP, get_diff(IP, new_IP) - 1);
        } else {
            type = 0;
        }
        indexes[0] = init_inst(type, buf);
        if (type) {
            for (int i = 1; i < indexes[0]->branch_no; i ++)
                indexes[0]->indexes[i] = indexes[i];
        move_stream(IP, get_diff(IP, new_IP) - 1);
        }
    }
    return head->indexes[0];
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

int get_parsable_length(stream_t *IP) {
    stream_t *old = malloc(sizeof(stream_t));
    *old = *IP;
    int diff;
    char buf[32] = "";
    LOG(DEBUG, "next:: %u", listench(IP));
    while (listench(IP)) {
        diff = bi_parsable(IP);
        LOG(INFO, "diff:: %d", get_diff(old, IP));
        if (diff) {
            LOG(DEBUG, "inloop:: %d", diff);
        } else break;
    }

    LOG(DEBUG, "diff:: %d", get_diff(old, IP));
    getstr(old, get_diff(old, IP), buf);
    for (int i = 0; i < 32; i ++)
        printf("%d ", buf[i]);
    puts("");
    int len = strlen(buf);
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
    free(old);
    return pars_len;
}
