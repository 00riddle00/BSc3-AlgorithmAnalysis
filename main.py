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


# ===============================================
# Utility functions
# ===============================================

# convert one-indexed to zero-indexed
# ind = index
def ind(index):
    return index - 1


def print_M(matrix_name, M):
    print(f'{matrix_name} = ')
    for row in M:
        print('    ', row)
    print('\n')


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
# Debug functions for blocks
# ==============================================================

def debug_block_1():
    debug_block_name(1)
    block_1()
    debug('Input (distance matrix):\n')
    debug_M('C', C)


def debug_block_2():
    debug_block_name(2)
    block_2()
    debug(f'Bound(Root) = {X[1]}\n')
    debug_M('C_prime', C_prime)


def debug_block_3():
    debug_block_name(3)
    block_3()
    debug(f'Child vertices: Y = ("{Y[0][0]},{Y[0][1]}"), Y_bar = ("{Y_bar[0][0]},{Y_bar[0][1]})_bar"')
    debug(f'from: i = {i_from}, to: j = {j_to}')
    debug(f'max_Dij = {max_Dij}\n')


def debug_block_4():
    debug_block_name(4)
    block_4()
    debug(f'Bound("({i_from},{j_to})_bar") = {Y_bar[1]}\n')


def debug_block_5():
    debug_block_name(5)
    block_5()
    debug(f'Bound("({i_from},{j_to})") = {Y[1]}\n')
    debug_M('C_prime', C_prime)


def debug_block_6():
    debug_block_name(6)
    is_matrix_simple = block_6()
    size = len(C_prime)
    if is_matrix_simple:
        debug(f'Matrix is simple enough (size = {size}x{size})\n')
    else:
        debug(f'Matrix is not simple enough (size = {size}x{size})\n')
    return is_matrix_simple


# ==============================================================
# Main program blocks
# ==============================================================

# ===============================================
# Block 1: Input data
# ===============================================

def block_1():
    global C
    # convert zeroes to infinity (=None)
    # let x mean a single element in a row
    C_tmp = []
    for row in C:
        C_tmp.append([None if x == 0 else x for x in row])

    C = C_tmp


# ===============================================
# Block 2: Matrix simplification and finding
#          the bound of the root vertex
# ===============================================

def block_2():
    global C, C_prime, tree, X
    C_prime = [row[:] for row in C]
    C_prime, bound_root = simplify(C_prime)
    X[1] = bound_root
    tree.append(X)


# ===============================================
# Block 3: Choosing the next vertex "(i,j)" for branching
# ===============================================

def block_3():
    global C_prime, i_from, j_to, max_Dij, Y, Y_bar
    # calculate the change of bound for all
    # elements in the matrix whose value is 0
    C_prime_T = transpose(C_prime)
    max_Dij = 0

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

    Y[0] = (i_from, j_to)
    Y_bar[0] = (i_from, j_to)


# ===============================================
# Block 4: Branching - finding the bound of
#          the vertex "(i,j)_bar"
# ===============================================

def block_4():
    global Y_bar, X, max_Dij
    bound_Y_bar = X[1] + max_Dij
    Y_bar[1] = bound_Y_bar


# ===============================================
# Block 5: Branching - finding the bound of
#          the vertex "(i,j)"
# ===============================================

def block_5():
    global C_prime

    # TODO indices should be queried if they still exist (here they don't)

    # TODO wrap in a function
    C_prime = C_prime[:ind(i_from)] + C_prime[ind(i_from) + 1:]

    C_prime_T = transpose(C_prime)
    C_prime_T = C_prime_T[:ind(j_to)] + C_prime_T[ind(j_to) + 1:]
    C_prime = transpose(C_prime_T)

    C_prime, sum_subtrahends = simplify(C_prime)

    bound_Y = X[1] + sum_subtrahends
    Y[1] = bound_Y


# ===============================================
# Block 6: Is the distance matrix small enough?
# ===============================================

# check matrix dimensions
def block_6():
    global C_prime
    return len(C_prime) == 2


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

    C_prime = None

    tree = []

    X = [(None, None), -1]
    Y = [(0, 0), -1]
    Y_bar = [(0, 0), -1]

    current_root = None
    current_vertex = None
    next_vertex = None

    i_from = None
    j_to = None
    max_Dij = None

    z_0 = None
    best_tour = []

    # ==============================================
    # Main loop
    # ==============================================

    debug_block_1()
    debug_block_2()
    debug_block_3()
    debug_block_4()
    debug_block_5()

    if debug_block_6():
        pass  # go to block 7
    else:
        pass  # go to block 9
