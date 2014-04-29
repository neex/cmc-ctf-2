#!/bin/bash

FLAG="MSUCTF__SEEMS_LIKE_THIS_STREAM_IS_HACKED" 
REPL="<flag output was suppressed"

if [ ${#FLAG}  <  $(( 1 + ${#REPL} )) ]; then
    echo "flag is too short"
    exit 1;
fi    

echo "Compiling cipher..."

if ! gcc stream.c -o stream; then 
    echo "Compilation failed"
    exit 1
fi    

echo "Preparing crypted files..."

dd if=/dev/urandom of=prefix bs=50 count=1 2> /dev/null
dd if=/dev/urandom of=suffix bs=50 count=1 2> /dev/null 

(cat prefix; echo -n $FLAG; cat suffix) | ./stream > encrypted_data.bin

(cat prefix; echo -n $REPL; for i in `seq $(( ${#FLAG} - 1 - ${#REPL}))`; do echo -n .;done; echo -n ">"; cat suffix ) > data.bin

rm -rf prefix suffix

echo "Compiling solution..."

if ! gcc solution.c -o solution; then 
    echo "Solution compilation failed"
    exit 1
fi    

echo "Checking if solution can decrypt flag..."
`which time` -f "%C finished in %E" ./solution | grep -q "$FLAG" || { 
    echo "Something wrong!!! Solution can't decrypt flag"; 
    exit 1
}

echo "All is ok!"
