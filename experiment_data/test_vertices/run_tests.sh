#!/usr/bin/env bash

# Test n1
for ((i=3;i<=207;i++)); 
do
    ./tsp_branch_bound.py -c $i -w 1 10 -r 1 -t 10 -s
    if [ $? -ne 0 ]; then exit $?; fi
done

# Test n2
for ((i=3;i<=207;i++)); 
do
    ./tsp_branch_bound.py -c $i -w 1000 100000 -r 1 -t 10 -s
    if [ $? -ne 0 ]; then exit $?; fi
done
