CC = gcc
LIBS_PATH=/usr/local/lib
LDFLAGS=-L$(LIBS_PATH) -L.
.PHONY: all
all: magneto

magneto: magneto.cpp
	$(CC) $(LDFLAGS) -Wall -O2 magneto.cpp -o magneto -llsm9ds1 -lwiringPi -lvl6180_pi

clean:
	rm -f magneto
