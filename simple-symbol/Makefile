CC = gcc
#CFLAGS = -Wall
LIBS = -lm

all: io environ parse ss
	$(CC) $(CFLAGS) *.o -o ss $(LIBS)

test: io environ parse ss-without-main _test
	$(CC) $(CFLAGS) *.o -o test $(LIBS)

environ: environ.c
	$(CC) $(CFLAGS) -c $< $(LIBS)

parse: parse.c
	$(CC) $(CFLAGS) -c $< $(LIBS)

io: io.c
	$(CC) $(CFLAGS) -c $< $(LIBS)

ss: environ parse io
	$(CC) $(CFLAGS) -c $< $(LIBS)
	$(CC) $(CFLAGS) *.o -o ss

ss-without-main: 
	@awk '/int main(.*) {/ { exit(0) };//' ss.c > _tmp.c
	$(CC) $(CFLAGS) -c _tmp.c $(LIBS)
	@rm _tmp.c

_test:
	$(CC) $(CFLAGS) -c test.c $(LIBS)

clean:
	rm -f *.o ss test
