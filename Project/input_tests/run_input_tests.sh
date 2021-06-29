#!/usr/bin/env bash

for i in {01..10};
do
    ./tsp_branch_bound.py "./input_test_$i"
    if [ $? -ne 0 ]; then exit $?; fi
done
