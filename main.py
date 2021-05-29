#!/usr/bin/env python

# ===============================================
# Global variables
# ===============================================
DEBUG = True


# ==============================================================
# Debug functions
# ==============================================================

def debug(text):
    global DEBUG
    if DEBUG:
        print(text)


def debug_M(matrix_name, M):
    global DEBUG
    if DEBUG:
        print_M(matrix_name, M)


def debug_block_name(block_no):
    global DEBUG
    if DEBUG:
        print('=========================')
        print(f'Block {block_no}')
        print('=========================\n')


def print_M(matrix_name, M):
    print(f'{matrix_name} = ')
    for row in M:
        print('    ', row)
    print('\n')


# ==============================================================
# Debug functions for blocks
# ==============================================================

def debug_block_1(C):
    debug_block_name(1)
    C = block_1(C)
    debug('Input (distance matrix):\n')
    debug_M('C', C)
    return C


# ===============================================
# Utility functions
# ===============================================


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


# ==============================================================
# Main program blocks
# ==============================================================

# ===============================================
# Block 1: Input data
# ===============================================

def block_1(M):
    # convert zeroes to infinity (=None)
    # let x mean a single element in a row
    M_new = []
    for row in M:
        M_new.append([None if x == 0 else x for x in row])

    return M_new


# ==============================================================
# Main code
# ==============================================================

if __name__ == '__main__':
    # ==============================================
    # Input
    # ==============================================

    # distance (between cities) matrix 'C'
    #         col no.  1    2    3   ...   n
    # row no.
    #   1            (a_11 a_12 a_13 ... a_1n)
    #   2            (a_21 a_22 a_23 ... a_2n)
    #   3            (a_31 a_32 a_33 ... a_3n)
    #  ...
    #   n            (an_1 an_2 an_3 ... a_nn)

    C = [[0, 1, 21, 27, 5],
         [30, 0, 18, 23, 23],
         [27, 29, 0, 20, 10],
         [15, 2, 27, 0, 14],
         [28, 9, 15, 6, 0]]

    # ==============================================
    # Setting up variables
    # ==============================================

    tree = 'tree'
    current_root = 'root'
    current_vertex = None
    next_vertex = None

    z_0 = None
    best_tour = None

    # ==============================================
    # Main loop
    # ==============================================

    C = debug_block_1(C)
