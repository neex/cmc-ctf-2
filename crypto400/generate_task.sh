#!/bin/bash

FLAG="MSUCTF__SEEMS_LIKE_THIS_STREAM_CIPHER_WAS_HACKED" 
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


(cat text.txt; echo -n $FLAG; echo) | ./stream > encrypted_data.bin

(cat text.txt; echo -n $REPL; for i in `seq $(( ${#FLAG} - 1 - ${#REPL}))`; do echo -n .;done; echo -n ">"; echo ) > plain.txt

rm -rf text

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
