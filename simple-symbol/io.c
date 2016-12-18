#include "io.h"

char getch(stream_t *stream) {
    if (stream->type == 'c')
        return *stream->stream.str++;
    else
        return getc(stream->stream.file);
}

char *getstr(stream_t *stream, int length) {
    char *buf = malloc(length * sizeof(char));
    for (int i = 0; i < length; i ++)
        buf[i] = getch(stream);
    return buf;
}

void move_stream(stream_t *stream, int diff) {
    if (stream->type == 'c')
        stream->stream.str += diff;
    else
        fseek(stream->stream.file, diff, SEEK_CUR);
}
