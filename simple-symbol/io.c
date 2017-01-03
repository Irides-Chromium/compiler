#include "io.h"

void LOG(err_level lvl, char *fmt, ...) {
    switch (lvl) {
        case VERBOSE:
            if (lvl < LOG_LEVEL) goto to_exit;
            fprintf(stderr, "%s", "Verbose: ");
            break;
        case INFO:
            if (lvl < LOG_LEVEL) goto to_exit;
            fprintf(stderr, "\x1b[32mInfo: \x1b[0m");
            break;
        case DEBUG:
            if (lvl < LOG_LEVEL) goto to_exit;
            fprintf(stderr, "\x1b[33mDebug: \x1b[0m");
            break;
        case WARNING:
            if (lvl < LOG_LEVEL) goto to_exit;
            fprintf(stderr, "\x1b[1;35mWarning: \x1b[0m");
            break;
        case ERROR:
            if (lvl < LOG_LEVEL) goto to_exit;
            fprintf(stderr, "\x1b[1;31mERROR: \x1b[0m");
            break;
    }

    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);

to_exit:;
    int stat = lvl - ERR_THRESHOLD + 1;
    if (stat > 0)
        exit(stat);
}

stream_t *init_stream(char type, char *string) {
    stream_t *stream = malloc(sizeof(stream_t));
    if (type == 's') {
        stream->type = 's';
        stream->str = string;
        stream->end = string + strlen(string);
    } else if (type == 'f') {
        stream->type = 'f';
        FILE *f;
        if (strcmp("stdin", string) == 0)
            f = stdin;
        else
            f = fopen(string, "r");
        if (f == NULL)
            LOG(ERROR, "No such file: %s", string);
        stream->file = f;
    }
    return stream;
}

char listench(stream_t *stream) {
    char ch = getch(stream);
    move_stream(stream, -1);
    return ch;
}

char getch(stream_t *stream) {
    if (stream->type == 's') {
        if (stream->str > stream->end)
            return EOF;
        else
            return *stream->str++;
    } else
        return getc(stream->file);
}

void getstr(stream_t *stream, int length, char *buf) {
    for (int i = 0; i < length; i ++)
        buf[i] = getch(stream);
}

long findch(stream_t *stream, char ch) {
    long start, end;
    end = start = getpos(stream);
    char c;
    while ((c = getch(stream)) != ch) {
        if (c == EOF) {
            end = -1;
            break;
        }
    }
    if (end != -1)
        end = getpos(stream) - 1;
    setpos(stream, start);
    return end;
}

void move_stream(stream_t *stream, int diff) {
    setpos(stream, diff + getpos(stream));
}

long getpos(stream_t *stream) {
    if (stream->type == 'f')
        return ftell(stream->file);
    else if (stream->type == 's')
        return (long) stream->str;
}

void setpos(stream_t *stream, long pos) {
    if (stream->type == 'f')
        fseek(stream->file, pos, SEEK_SET);
    else if (stream->type == 's') {
        stream->str = (char *) pos;
    }
}

int get_diff(stream_t *s1, stream_t *s2) {
    if (s1->type == 's' && s2->type == 's')
        return s2->str - s1->str;
    else if (s1->type == 'f' && s2->type == 'f')
        return ftell(s2->file) - ftell(s1->file);
    else
        LOG(ERROR, "Different types for ``get_diff'' @ %s %d", __FILE__, __LINE__);
}

void close_stream(stream_t *stream) {
    if (stream->type == 's') {
        /* Hard to determine whether to free the buffer, free it outside the func. */
        //if (stream->str > (char *) 0x500000)
        //    free(stream->str);
    } else
        fclose(stream->file);
    free(stream);
}
