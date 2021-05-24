#!/usr/bin/env python

# ===============================================
# Global variables
# ===============================================
DEBUG = False


# ===============================================
# Utility functions
# ===============================================
def debug(text):
    global DEBUG
    if DEBUG:
        print(text)


def print_M(M):
    for row in M:
        print('    ', row)


# convert one-indexed to zero-indexed
# ind = index
def ind(index):
    return index - 1


# find minimum ignoring None values
def min_no_none(row):
    return min([x for x in row if (x is not None)])


# find minimum ignoring one element
# (by its index)
def min_no_element(row, index):
    row = row[:index] + row[index + 1:]
    return min_no_none(row)


# M = matrix
def transpose(M):
    return list(map(list, zip(*M)))


# subtract all elements in a row by
# the smallest value in that row
def subtract_min(M):
    subs = 0
    for i, row in enumerate(M):
        # min_x = min([x for x in row if x is not None])
        min_x = min_no_none(row)
        subs += min_x
        M[i] = [(x - min_x) if x is not None else None for x in row]
    return M, subs


# ===============================================
# Main program functions
# ===============================================

def simplify(M):
    # we collect all the numbers that were
    # subtracted from rows and columns
    sum_subtrahends = 0

    # apply one run of subtraction on rows
    M, sum_subs = subtract_min(M)
    sum_subtrahends += sum_subs

    # apply one run of subtraction on columns
    # We transpose M to get M_T
    M_T = transpose(M)
    M_T, sum_subs = subtract_min(M_T)
    sum_subtrahends += sum_subs
    M = transpose(M_T)

    return M, sum_subtrahends


# ===============================================
# Block 1: Input data
# ===============================================
print('=========================')

# distance (between cities) matrix 'C'
#         col no.  1    2    3   ...   n
# row no.
#   1            (a_11 a_12 a_13 ... a_1n)
#   2            (a_21 a_22 a_23 ... a_2n)
#   3            (a_31 a_32 a_33 ... a_3n)
#  ...
#   n            (an_1 an_2 an_3 ... a_nn)
#
C = [[0, 1, 21, 27, 5],
     [30, 0, 18, 23, 23],
     [27, 29, 0, 20, 10],
     [15, 2, 27, 0, 14],
     [28, 9, 15, 6, 0]]

print('C = ')
print_M(C)

# ===============================================
# Block 2: Matrix simplification,
#          finding the bound of the root vertex
# ===============================================
print('=========================')

# convert zeroes to infinity (=None)
# let x mean a single element in a row
C_prime = []
for row in C:
    C_prime.append([None if x == 0 else x for x in row])

debug(C_prime)

C_prime, sum_subtrahends = simplify(C_prime)

# get the (lower) bound
# of the root vertex
bound_root = sum_subtrahends

print(f'Bound(Root) = {bound_root}\n')
print('C\' = ')
print_M(C_prime)

# ===============================================
# Block 3: Choosing the next vertex for branching
# ===============================================
print('=========================')

# calculate the change of bound for all
# elements in the matrix whose value is 0
C_prime_T = transpose(C_prime)
max_Dij = 0
i_from = None
j_to = None

for i, row in enumerate(C_prime, 1):
    for j, el in enumerate(row, 1):
        if el == 0:
            # i-th row and j-th column element is zero
            # hence there is no path i -> j, meaning there are
            # such paths 1 -> k and l -> 2 where k != 2 and l != 1.
            # For every such path their bound will increase by
            # the size D[i,j] = min(i-th row without j-th element) + min(j-th column without i-th element)
            D_ij = min_no_element(C_prime[ind(i)], ind(j)) + min_no_element(C_prime_T[ind(j)], ind(i))
            # TODO change '>=' to '=' and 'LAST' to 'FIRST'
            # if there are more than one maximum value,
            # we choose the LAST one encountered as maximum
            if D_ij >= max_Dij:
                max_Dij = D_ij
                i_from = i
                j_to = j
            debug(D_ij)

# ===============================================
# Block 4: Branching - finding the bound of
#          the vertex "not(i,j)"
# ===============================================
debug('=========================')
debug(i_from)
debug(j_to)
debug('=========================')

bound_not_ij = bound_root + max_Dij

print(f'Bound("NOT(ij)") = {bound_not_ij}\n')
print('C\' = ')
print_M(C_prime)

# ===============================================
# Block 5: Branching - finding the bound of
#          the vertex "(i,j)"
# ===============================================
print('=========================')

debug(C_prime)

C_prime[ind(j_to)][ind(i_from)] = None
debug(C_prime)

C_prime = C_prime[:ind(i_from)] + C_prime[ind(i_from) + 1:]
debug(C_prime)

C_prime_T = transpose(C_prime)
C_prime_T = C_prime_T[:ind(j_to)] + C_prime_T[ind(j_to) + 1:]
C_prime = transpose(C_prime_T)
debug(C_prime)

C_prime, sum_subtrahends = simplify(C_prime)
bound_ij = bound_root + sum_subtrahends

print(f'Bound("(ij)") = {bound_ij}\n')
print('C\' = ')
print_M(C_prime)
