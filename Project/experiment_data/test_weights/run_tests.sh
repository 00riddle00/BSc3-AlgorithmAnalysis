#!/usr/bin/env bash

c=10  # Test w1
#c=20  # Test w2
#c=30  # Test w3
#c=40  # Test w4
#c=50  # Test w5
#c=100 # Test w10

# part 1
for ((i=10;i<=100;i=i+10)); 
do
    ./tsp_branch_bound.py -c $c -w 1 $i -r 1 -t 10 -s
    if [ $? -ne 0 ]; then exit $?; fi
done

echo

# part 2
for ((i=200;i<=1000;i=i+100)); 
do
    ./tsp_branch_bound.py -c $c -w 1 $i -r 1 -t 10 -s
    if [ $? -ne 0 ]; then exit $?; fi
done

echo

# part 3
for ((i=2000;i<=100000;i=i+1000)); 
do
    ./tsp_branch_bound.py -c $c -w 1 $i -r 1 -t 10 -s
    if [ $? -ne 0 ]; then exit $?; fi
done

echo

# part 4
for ((i=200000;i<=10000000;i=i+100000)); 
do
    ./tsp_branch_bound.py -c $c -w 1 $i -r 1 -t 10 -s
    if [ $? -ne 0 ]; then exit $?; fi
done
