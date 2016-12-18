#ifndef _PARSE_H
#   define _PARSE_H

#include <regex.h>
#include <string.h>
#include "io.h"
#include "environ.h"

extern char *RETN, *RECI, *OPER, *L_BRAC, *ALL, *BI_PAR, *OPER, *MATH_OP, *RETN, *EITHER, *RECI, *BRAC, *L_BRAC, *R_BRAC;

int bi_parsable(stream_t stream);
char *get_parsable_length(stream_t stream);

ss_inst *init_inst(char type, char *expr);
bool inst_has_mid(ss_inst *self);
ss_inst *inst_get_index(ss_inst *self, pos_t pos);
ss_inst **inst_get_indexes(ss_inst *self);
ss_inst *inst_get_other_end(ss_inst *self);
void inst_set_index(ss_inst *self, pos_t pos, ss_inst *index);
void inst_set_indexes(ss_inst *self, ss_inst **indexes);
void inst_set_other_end(ss_inst *self, ss_inst *index);
void print_inst(ss_inst *self);

#endif /* _PARSE_H */
