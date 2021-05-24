#!/usr/bin/env python

# ===================================
# Utility functions
# ===================================

# convert one-indexed to zero-indexed
def index(ind):
    return ind - 1


# find minimum ignoring None values
def min_no_none(row):
    return min([x for x in row if (x is not None)])


# find minimum ignoring one element
# (by its index)
def min_no_element(row, index):
    row = row[:index] + row[index + 1:]
    return min_no_none(row)


# subtract all elements in a row by
# the smallest value in that row
def subtract_min(matrix):
    subs = 0
    for i, row in enumerate(matrix):
        # min_x = min([x for x in row if x is not None])
        min_x = min_no_none(row)
        subs += min_x
        matrix[i] = [(x - min_x) if x is not None else None for x in row]
    return matrix, subs


# ===================================
# Input data
# ===================================

# distance (between cities) matrix 'c'
#         col no.  1    2    3  ...   n
# row no.
#   1            (a_11 a_12 a_13 ... a_1n)
#   2            (a_21 a_22 a_23 ... a_2n)
#   3            (a_31 a_32 a_33 ... a_3n)
#   ...
#   n            (an_1 an_2 an_3 ... a_nn)
#
c = [[0, 1, 21, 27, 5],
     [30, 0, 18, 23, 23],
     [27, 29, 0, 20, 10],
     [15, 2, 27, 0, 14],
     [28, 9, 15, 6, 0]]

print(c)

# ===================================
# Matrix simplification
# ===================================

# convert zeroes to infinity (=None)
# let x mean a single element in a row
c_prime = []
for row in c:
    c_prime.append([None if x == 0 else x for x in row])

print(c_prime)

# we collect
sum_subtrahends = 0

# apply one run of subtraction on rows
c_prime, sum_subs = subtract_min(c_prime)
sum_subtrahends += sum_subs

print(c_prime)

# apply one run of subtraction on columns
# We transpose C_prime to get C_prime_T
c_prime_T = list(map(list, zip(*c_prime)))
c_prime_T, sum_subs = subtract_min(c_prime_T)
sum_subtrahends += sum_subs
c_prime = list(map(list, zip(*c_prime_T)))

print(c_prime)

# get the (lower) bound
# of the root vertex
bound_root = sum_subtrahends

print(bound_root)

# ===================================
# Branching of the decision tree
# ===================================

print("=========================")

# calculate the change of bound for all
# elements in the matrix whose value is 0
for i, row in enumerate(c_prime, 1):
    for j, el in enumerate(row, 1):
        if el == 0:
            # i-th row and j-th column element is zero
            # hence there is no path i -> j, meaning there are
            # such paths 1 -> k and l -> 2 where k != 2 and l != 1.
            # For every such path their bound will increase by
            # the size D[i,j] = min(i-th row without j-th element) + min(j-th column without i-th element)
            D_ij = min_no_element(c_prime[index(i)], index(j)) + min_no_element(c_prime_T[index(j)], index(i))
            print(D_ij)
