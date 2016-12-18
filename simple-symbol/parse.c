#include "parse.h"
#include "environ.h"

ss_inst *init_inst(char type, char *expr) {
    ss_inst *self = malloc(sizeof(ss_inst));
    self->type = type;
    strncpy(self->expr, expr, 8);

    int branch_no;
    switch (type) {
        case '?': branch_no = 4; break;
        case 'w': branch_no = 3; break;
        case '[':
        case '{':
        case '(': branch_no = 2; break;
        default: branch_no = 1; break;
    }
    self->indexes = malloc(branch_no * sizeof(ss_inst *));
    return self;
}

//void print_inst(ss_inst *self) {
//    printf("<%c@", self->byte);
//    for (int i = 0; i < 3; i ++) {
//        char pos[4];
//        if (self->indexes[i] == NULL)
//            sprintf(pos, "   ");
//        else
//            sprintf(pos, "%3d", self->indexes[i]);
//
//        printf(i == self->pos ? "\x1b[46m%s\x1b[0m" : "%s", pos);
//
//        if (i < 2)
//            printf("|");
//    }
//    printf("\n");
//}

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
    char *expr = getstr(stream, 4);
    move_stream(stream, -4);
    regex_t *pattern = malloc(sizeof(regex_t));
    int cflags = REG_EXTENDED;
    char buf[64];
    int len = 1;
    /* Conditional start                     |  RETNs   |*/
    regcomp(pattern, "^\\?(>=|==|<=|>>|<<|/=)[~@#$:(`|_&]", cflags);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 4;
        goto end;
    }

    regfree(pattern);
    /* Conditional start simplified */
    regcomp(pattern, "^\\?(>=|==|<=|>>|<<|/=).", cflags);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 3;
        goto end;
    }

    regfree(pattern);
    /* Conditional else or end */
    regcomp(pattern, "^\\?[!$]", cflags);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        len = 2;
        goto end;
    }

    regfree(pattern);
    /* RECI & RETN */
    /*                 | OPER  ||  RECI  ||   RETN   | */
    regcomp(pattern, "^[-+*/^%<>~#$@!:;.=][~@#$:(`|_&]", cflags);
    if (!regexec(pattern, expr, 0, 0, 0)) {
        regfree(pattern);
        /* NOT two operators */
        /*                 |  OPER  ||  OPER  | */
        regcomp(pattern, "^[-+*/^%<>][-+*/^%<>]", cflags);
        if (regexec(pattern, expr, 0, 0, 0))
            len = 2;
    }

end:
    regfree(pattern);
    free(pattern);
    move_stream(stream, len);
    return len;
}

/* get_parsable_length:
 * @param char *expr: the pointer of the Instruction Pointer
 * @return: the maximum parsable length
 */

char *get_parsable_length(stream_t *stream) {
    char *IP = stream.stream.str;
    char *new_IP = IP;
    while (*new_IP) {
        stream_t stream1;
        stream1.stream.str = new_IP;
        int diff = bi_parsable(stream1);
        if (diff) new_IP += diff - 1;
        else break;
    }

    char buf[32];
    snprintf(buf, new_IP - IP, "%s", IP);
    regmatch_t *match = malloc(sizeof(regmatch_t));
    regex_t *pattern = malloc(sizeof(regex_t));
    regcomp(pattern, ".[~#].", 0);
    if (!regexec(pattern, buf, 1, match, 0)) {
        regfree(pattern);
        free(pattern);
        free(match);
        return IP + match->rm_so + 2;
    }
    regfree(pattern);
    free(pattern);
    free(match);
    return new_IP + 1;
}
