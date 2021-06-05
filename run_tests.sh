#!/usr/bin/env bash

for ((i=3;i<=200;i++)); 
do
    ./main.py -c$i -w 1 10
    if [ $? -ne 0 ]; then exit $?; fi
done
