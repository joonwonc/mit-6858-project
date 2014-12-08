ASFLAGS := -m32
CFLAGS  := -m32 -g -std=c99 -Wall -Werror -D_GNU_SOURCE
LDFLAGS := -m32
LDLIBS  := -lcrypto
PROGS   := zookld zookfs zookd

all: $(PROGS)
.PHONY: all

zookld zookd zookfs: %: %.o http.o

.PHONY: check
check: $(PROGS)
	./check-bug2.sh

.PHONY: clean
clean:
	rm -f *.o *.pyc *.bin $(PROGS)


