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
    global DEBUG, iteration
    if DEBUG:
        print('=========================')
        print(f'Block {block_no} (iteration {iteration})')
        print('=========================\n')


# ===============================================
# Utility functions
# ===============================================

# =======================================
# Functions which do not
# change program variables
# =======================================

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


# =======================================
# Functions using program variables
# =======================================

def print_solution():
    global best_tour
    print('=========================')
    print(f'Solution:')
    print('=========================\n')
    for v in best_tour[:-1]:
        print(f'{v} ->', end=' ')
    print(best_tour[-1])
    print(f'\nCost = {best_cost}')


# =======================================
# Functions changing program variables
# =======================================

def reset_C_prime():
    global C_prime
    C_prime = [row[:] for row in C]
    reset_row_col_map()


def reset_row_col_map():
    global C_prime, row_map, col_map

    row_map = [i for i in range(1, len(C_prime) + 1)]
    col_map = [i for i in range(1, len(C_prime) + 1)]


def delete_row_col(i_row, j_col):
    global C_prime
    # delete i-th row
    C_prime = C_prime[:row_map.index(i_row)] + C_prime[(row_map.index(i_row) + 1):]

    # delete j-th column
    C_prime_T = transpose(C_prime)
    C_prime_T = C_prime_T[:col_map.index(j_col)] + C_prime_T[(col_map.index(j_col) + 1):]
    C_prime = transpose(C_prime_T)

    fix_map_on_delete(i_row, j_col)


def fix_map_on_delete(row_from_map, col_from_map):
    global row_map, col_map

    row_index = row_map.index(row_from_map) + 1
    row_map.pop(ind(row_index))

    col_index = col_map.index(col_from_map) + 1
    col_map.pop(ind(col_index))


def disable_path(i_row, j_col):
    global row_map, col_map
    if i_row in row_map and j_col in col_map:
        C_prime[row_map.index(i_row)][col_map.index(j_col)] = None


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
    debug(f'Child vertices: Y_bar = ("{Y_bar[0][0]},{Y_bar[0][1]}"), Y = ("{Y[0][0]},{Y[0][1]}")')
    debug(f'from: i = {i_from}, to: j = {j_to}')
    debug(f'max_Dij = {max_Dij}\n')


def debug_block_4():
    debug_block_name(4)
    block_4()
    debug(f'Bound("({-i_from},{-j_to})") = {Y_bar[1]}\n')


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


def debug_block_7():
    debug_block_name(7)
    block_7()
    debug(f'Current tour: {current_tour}')  # todo
    debug(f'Bound("Y_last") = {Y[1]}\n')  # todo


def debug_block_8():
    debug_block_name(8)
    old_z_0 = z_0
    debug(f'z_0 before: {z_0}')

    block_8()

    debug(f'z_0 after: {z_0}')

    if z_0 != old_z_0:
        debug(f'Better tour has been found: {best_tour}\n')
    else:
        debug(f'We did not find a better tour. Best tour so far: {best_tour}\n')


def debug_block_9():
    debug_block_name(9)
    block_9()
    i, j = X[0][0], X[0][1]
    debug(f'Next vertex: X = ("{i},{j}")')
    debug(f'Bound("({i},{j})") = {X[1]}\n')


def debug_block_10():
    debug_block_name(10)
    is_no_better_path = block_10()

    if is_no_better_path:
        debug('The current chosen vertex does not contain the better tour '
              'than we already have. The algorithm stops here.\n')
    else:
        if not len(best_tour):
            comment_on_best_tour = 'which is none so far'
        else:
            best_tour_bound = '= ?'
            comment_on_best_tour = f'bound={best_tour_bound}'
        debug(f'The current chosen vertex has a lower bound (= {X[1]}) than '
              f'the current best tour ({comment_on_best_tour}).')
        debug('Hence the algorithm proceeds.\n')

    return is_no_better_path


def debug_block_11():
    debug_block_name(11)
    bound_of_X = X[1]
    old_bound_of_X = bound_of_X

    block_11()

    bound_of_X = X[1]

    if old_bound_of_X == bound_of_X:
        debug('Same vertex has been picked as it was before,'
              ' the matrix C_prime does not change.\n')
        debug_M('C_prime', C_prime)
        debug('The bound of X is:')
        i, j = X[0][0], X[0][1]
        debug(f'Bound("({i},{j})") = {X[1]}\n')
    else:
        debug('Matrix has been corrected. It is now:')
        debug_M('C_prime', C_prime)

        debug('The bound of X has been updated. It is now:')
        i, j = X[0][0], X[0][1]
        debug(f'Bound("({i},{j})") = {X[1]}\n')


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
    global C, C_prime, tree, X, row_map, col_map, tree_len

    reset_C_prime()
    C_prime, bound_root = simplify(C_prime)
    X[1] = bound_root
    tree.append(X)
    tree_len = 1
    X[2] = 0


# ===============================================
# Block 3: Choosing the next vertex "(i,j)" for branching
# ===============================================

def block_3():
    global C_prime, i_from, j_to, max_Dij, Y, Y_bar, tree_len

    # reset these variables
    Y = [(0, 0), -1, -1, -1]
    Y_bar = [(-0, -0), -1, -1, -1]
    i_from = None
    j_to = None
    max_Dij = None

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
                # TODO change '>=' to '>' and 'LAST' to 'FIRST'
                # if there are more than one maximum value,
                # we choose the LAST one encountered as maximum

                # todo choose one of them
                # if D_ij >= max_Dij:
                if D_ij > max_Dij:
                    max_Dij = D_ij
                    i_from = row_map[ind(i)]
                    j_to = col_map[ind(j)]

    Y[0] = (i_from, j_to)
    Y_bar[0] = (-i_from, -j_to)

    Y_bar[2] = tree_len
    tree.append(Y_bar)
    tree_len += 1

    Y[2] = tree_len
    tree.append(Y)
    tree_len += 1


# ===============================================
# Block 4: Branching - finding the bound of
#          the vertex "(i,j)_bar"
# ===============================================

def block_4():
    global Y_bar, X, max_Dij, possible_vertices, possible_vertices_len
    bound_Y_bar = X[1] + max_Dij
    Y_bar[1] = bound_Y_bar
    # we always check Y first, so let's save Y_bar for later
    Y_bar[3] = possible_vertices_len
    possible_vertices.append(Y_bar)
    possible_vertices_len += 1


# ===============================================
# Block 5: Branching - finding the bound of
#          the vertex "(i,j)"
# ===============================================

def block_5():
    global C_prime

    delete_row_col(i_from, j_to)
    disable_path(j_to, i_from)
    C_prime, sum_subtrahends = simplify(C_prime)

    bound_Y = X[1] + sum_subtrahends
    Y[1] = bound_Y


# ===============================================
# Block 6: Is the distance matrix small enough?
# ===============================================

# check matrix dimensions
def block_6():
    global C_prime
    print("LEN=", len(C_prime))
    return len(C_prime) == 2


# ===============================================
# Block 7: Exhaustive estimation of the remaining matrix
# ===============================================

def block_7():
    global current_tour, C

    paths = []

    row_from = 0
    col_to = 0

    if (C_prime[0][0] is None) or \
            (C_prime[0][1] is not None and C_prime[0][0] > C_prime[0][1]):
        col_to = 1

    i_from = row_map[row_from]
    j_to = col_map[col_to]

    paths.append([i_from, j_to])

    row_from = 1
    col_to = (col_to + 1) % 2

    i_from = row_map[row_from]
    j_to = col_map[col_to]

    paths.append([i_from, j_to])

    # todo add full tree reading functionality
    curr_index = Y[2]
    for i in range(2, curr_index + 1, 2):
        paths.append([tree[i][0][0], tree[i][0][1]])

    current_tour = []
    cost = 0

    start_el = 1
    while paths:
        for i, path in enumerate(paths):
            if path[0] == start_el:
                cost += C[ind(path[0])][ind(path[1])]
                current_tour.append(start_el)
                start_el = path[1]
                paths.pop(i)

    # todo can there be bound_Y_bar at this point?
    #      or can we ever stop on Y_bar?
    Y[1] = cost


# ===============================================
# Block 8: Is bound_Y_last < z_0? If yes, save the
#          current tour as the best so far
# ===============================================

def block_8():
    global z_0, current_tour, best_tour, best_cost
    cost = Y[1]
    if z_0 is None or cost < z_0:
        z_0 = cost
        best_tour = current_tour
        best_cost = cost


# ===============================================
# Block 9: Choose the next vertex
# ===============================================

def block_9():
    global X, Y, possible_vertices, possible_vertices_len

    for Y_possible in possible_vertices:
        if Y_possible[1] < Y[1]:
            possible_vertices.pop(Y_possible[3])
            Y_possible[3] = -1
            possible_vertices_len -= 1

            X = Y_possible
        else:
            X = Y


# ===============================================
# Block 10: Do we have the best tour already?
# ===============================================

def block_10():
    global X, z_0
    bound_X = X[1]
    if z_0 is not None and z_0 <= bound_X:
        return True
    else:
        return False


# ===============================================
# Block 11: Correct matrix for current vertex X
# ===============================================

def block_11():
    global X, Y, C, C_prime, tree, tree_len, possible_vertices, possible_vertices_len

    # Is the next chosen vertex X the same as the curent vertex Y?
    # fixme
    if X[0] == Y[0]:
        # C_prime does not change, it's the same that we need
        return

    # traversing the tree
    node = X
    parent_nodes = []  # todo is it needed here?
    parent_index = -1
    included_paths = []
    excluded_paths = []

    while True:
        node_index = node[2]
        is_bar_vertex = node[0][0] < 0
        parent_index = node_index - 1
        if is_bar_vertex:
            excluded_paths.append(node[0])
        else:
            parent_index -= 1
            included_paths.append(node[0])
        if parent_index != 0:
            parent = tree[parent_index]
            parent_nodes.append(parent)
            node = parent
        else:
            break

    reset_C_prime()

    for path in excluded_paths:
        i_from = -path[0]
        j_to = -path[1]
        C_prime[row_map.index(i_from)][col_map.index(j_to)] = None

    cost_included_paths = 0

    for path in included_paths:
        i_from = path[0]
        j_to = path[1]

        # todo should we count excluded paths here as well?
        cost_included_paths += C[ind(i_from)][ind(j_to)]

        delete_row_col(i_from, j_to)
        disable_path(j_to, i_from)

    C_prime, sum_subtrahends = simplify(C_prime)

    # adjust bound(X) value
    X[1] = cost_included_paths + sum_subtrahends
    print(X[1])

    # todo adjust the tree
    # (...)


# ==============================================================
# Main code
# ==============================================================

if __name__ == '__main__':
    # ==============================================
    # Input
    # ==============================================

    # TODO read from a file
    # distance (between cities) matrix 'C'
    #         col no.  1    2    3   ...   n
    # row no.
    #   1            (a_11 a_12 a_13 ... a_1n)
    #   2            (a_21 a_22 a_23 ... a_2n)
    #   3            (a_31 a_32 a_33 ... a_3n)
    #  ...
    #   n            (an_1 an_2 an_3 ... a_nn)

    # C = [[0, 1, 21, 27, 5],
    #      [30, 0, 18, 23, 23],
    #      [27, 29, 0, 20, 10],
    #      [15, 2, 27, 0, 14],
    #      [28, 9, 15, 6, 0]]

    C = [[0, 25, 40, 31, 27],
         [5, 0, 17, 30, 25],
         [19, 15, 0, 6, 1],
         [9, 50, 24, 0, 6],
         [22, 8, 7, 10, 0]]

    # ==============================================
    # Setting up variables
    # ==============================================

    C_prime = None

    row_map = []
    col_map = []

    tree = []
    tree_len = 0
    possible_vertices = []
    possible_vertices_len = 0

    # [ ('i', 'j'), bound, place in the tree, place in the list of possible vertices]
    X = [(None, None), -1, -1, -1]
    Y = [(0, 0), -1, -1, -1]
    Y_bar = [(-0, -0), -1, -1, -1]

    i_from = None
    j_to = None
    max_Dij = None

    z_0 = None
    current_tour = []
    best_tour = []
    best_cost = -1

    # ==============================================
    # Main loop
    # ==============================================

    iteration = 1

    debug_block_1()
    debug_block_2()

    # todo add check: iter_max
    while True:
        debug_block_3()
        debug_block_4()
        debug_block_5()

        if debug_block_6():
            debug_block_7()
            debug_block_8()

        debug_block_9()

        if not debug_block_10():
            debug_block_11()
        else:
            break

        iteration += 1

    # TODO print to a file
    print_solution()
