#include <stdio.h>
#include <malloc.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>

#ifndef _IO_H
#   define _IO_H

typedef struct {
    char type;
    union {
        FILE *file;
        struct {
            char *str;
            char *end;
        };
    };
} stream_t;

typedef enum {
    VERBOSE = 0,
    INFO,
    DEBUG,
    WARNING,
    ERROR
} err_level;

#ifndef ERR_THRESHOLD
#   define ERR_THRESHOLD WARNING
#endif

#ifndef LOG_LEVEL
#   define LOG_LEVEL WARNING
#endif

void LOG(err_level lvl, char *fmt, ...);

stream_t *init_stream(char type, char *string);
char getch(stream_t *stream);
char listench(stream_t *stream);
void getstr(stream_t *stream, int length, char *buf);
void move_stream(stream_t *stream, int diff);
long findch(stream_t *stream, char ch);
long getpos(stream_t *stream);
void setpos(stream_t *stream, long pos);
int get_diff(stream_t *s1, stream_t *s2);
void close_stream(stream_t *stream);

#endif /* _IO_H */
