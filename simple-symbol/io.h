#include <stdio.h>
#include <malloc.h>

#ifndef _IO_H
#   define _IO_H

typedef struct {
    char type;
    union {
        char *str;
        FILE *file;
    } stream;
} stream_t;

char getch(stream_t *stream);
char *getstr(stream_t *stream, int length);
void move_stream(stream_t *stream, int diff);

#endif /* _IO_H */
