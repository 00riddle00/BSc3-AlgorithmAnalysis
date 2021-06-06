#!/usr/bin/env bash

for i in {01..10};
do
    ./tsp_branch_bound.py "tests/inputs/input_test_$i"
    #if [ $? -ne 0 ]; then exit $?; fi
done

for ((i=3;i<=200;i++)); 
do
    ./tsp_branch_bound.py -c$i -w 1 10
    if [ $? -ne 0 ]; then exit $?; fi
done
