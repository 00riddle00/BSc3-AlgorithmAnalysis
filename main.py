#!/usr/bin/env python

# ===============================================
# Global variables
# ===============================================
global DEBUG, \
    C_prime, row_map, col_map, i_from, j_to, max_Dij, \
    X, Y, Y_bar, candidate_nodes, z_0, current_tour, best_tour, best_cost, \
    iterations

DEBUG = False


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
    global DEBUG, iterations
    if DEBUG:
        print('=========================')
        print(f'Block {block_no} (iteration {iterations})')
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
    for v in best_tour:
        print(f'{v} ->', end=' ')
    print(best_tour[0])
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
# Functions for blocks with debug possibility
# ==============================================================

def debug_block_1():
    debug_block_name(1)
    block_1()
    debug('Input (distance matrix):\n')
    debug_M('C', C)


def debug_block_2():
    debug_block_name(2)
    block_2()
    debug(f'Bound(Root) = {X.bound}\n')
    debug_M('C_prime', C_prime)


def debug_block_3():
    debug_block_name(3)
    block_3()
    debug(f'Child vertices: Y_bar = ("{Y_bar.path[0]},{Y_bar.path[0]}"), Y = ("{Y.path[0]},{Y.path[0]}")')
    debug(f'from: i = {i_from}, to: j = {j_to}')
    debug(f'max_Dij = {max_Dij}\n')


def debug_block_4():
    debug_block_name(4)
    block_4()
    debug(f'Bound("({-i_from},{-j_to})") = {Y_bar.bound}\n')


def debug_block_5():
    debug_block_name(5)
    block_5()
    debug(f'Bound("({i_from},{j_to})") = {Y.bound}\n')
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
    debug(f'Current tour: {current_tour}')
    debug(f'Bound("Y_last") = {Y.bound}\n')


def debug_block_8():
    debug_block_name(8)
    old_z_0 = z_0

    block_8()

    if z_0 != old_z_0:
        debug(f'Better tour has been found: {best_tour}\n')
    else:
        debug(f'We did not find a better tour. Best tour so far: {best_tour}\n')


def debug_block_9():
    debug_block_name(9)
    block_9()
    i, j = X.path[0], X.path[1]
    debug(f'Next vertex: X = ("{i},{j}")')
    debug(f'Bound("({i},{j})") = {X.bound}\n')


def debug_block_10():
    debug_block_name(10)
    is_no_better_path = block_10()

    if is_no_better_path:
        debug('The current chosen vertex does not contain the better tour '
              'than we already have. The algorithm stops here.\n')
    else:
        best_tour_bound = 'infinity'
        if len(best_tour):
            best_tour_bound = f'{best_cost}'

        debug(f'The current chosen vertex has a lower bound (= {X.bound}) than '
              f'the current best tour (bound = {best_tour_bound}).')
        debug('Hence the algorithm proceeds.\n')

    return is_no_better_path


def debug_block_11():
    debug_block_name(11)
    is_the_same = block_11()

    if is_the_same:
        debug('Same vertex has been picked as it was before,'
              ' the matrix C_prime does not change.\n')
        debug_M('C_prime', C_prime)
        debug('The bound of X is:')
        i, j = X.path[0], X.path[1]
        debug(f'Bound("({i},{j})") = {X.bound}\n')
    else:
        debug('Matrix has been corrected. It is now:\n')
        debug_M('C_prime', C_prime)

        debug('The bound of X has been updated. It is now:')
        i, j = X.path[0], X.path[1]
        debug(f'Bound("({i},{j})") = {X.bound}\n')


# ==============================================================
# Solution tree imlementation
# ==============================================================

class Node:

    def __init__(self, parent, path, bound=None):
        self.parent = parent
        self.path = path
        self.left_child = None
        self.right_child = None
        self.bound = bound


class CandidateNodes:
    nodelist = []
    size = 0

    def add(self, node):
        for i in range(self.size):
            if node.bound <= self.nodelist[i].bound:
                self.nodelist.insert(i, node)
                self.size += 1
                return

        self.nodelist.append(node)
        self.size += 1

    def get(self):
        return self.nodelist[0]

    def pop(self):
        self.nodelist = self.nodelist[1:]
        self.size -= 1


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
    global X, C, C_prime, row_map, col_map

    reset_C_prime()
    C_prime, bound_root = simplify(C_prime)
    X = Node(None, (None, None), bound=bound_root)


# ===============================================
# Block 3: Choosing the next vertex "(i,j)" for branching
# ===============================================

def block_3():
    global Y, Y_bar, C_prime, i_from, j_to, max_Dij

    # reset these variables
    Y = [(0, 0), None, None, None, False]
    Y_bar = [(-0, -0), None, None, None, False]

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
                # if there are more than one maximum value,
                # we choose the first one encountered as maximum

                if D_ij > max_Dij:
                    max_Dij = D_ij
                    i_from = row_map[ind(i)]
                    j_to = col_map[ind(j)]

    Y_bar = Node(X, (-i_from, -j_to))
    Y = Node(X, (i_from, j_to))

    X.left_child = Y_bar
    X.right_child = Y


# ===============================================
# Block 4: Branching - finding the bound of
#          the vertex "(i,j)_bar"
# ===============================================

def block_4():
    global max_Dij, candidate_nodes
    Y_bar.bound = X.bound + max_Dij
    # we always check Y first, so let's save Y_bar for later
    candidate_nodes.add(Y_bar)


# ===============================================
# Block 5: Branching - finding the bound of
#          the vertex "(i,j)"
# ===============================================

def block_5():
    global X, Y, C_prime

    delete_row_col(i_from, j_to)
    disable_path(j_to, i_from)
    C_prime, sum_subtrahends = simplify(C_prime)

    Y.bound = X.bound + sum_subtrahends

    # reset X
    X = None


# ===============================================
# Block 6: Is the distance matrix small enough?
# ===============================================

# check matrix dimensions
def block_6():
    global C_prime
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

    paths.insert(0, [i_from, j_to])

    # traversing the tree
    node = Y

    while node.parent is not None:
        is_bar_vertex = node.path[0] < 0

        if not is_bar_vertex:
            paths.append([node.path[0], node.path[1]])

        node = node.parent

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

    Y.bound = cost


# ===============================================
# Block 8: Is bound_Y_last < z_0? If yes, save the
#          current tour as the best so far
# ===============================================

def block_8():
    global z_0, current_tour, best_tour, best_cost
    cost = Y.bound
    if z_0 is None or cost < z_0:
        z_0 = cost
        best_tour = current_tour
        best_cost = cost


# ===============================================
# Block 9: Choose the next vertex
# ===============================================

def block_9():
    global X, Y, C_prime, candidate_nodes

    X = Y

    candidate_node = candidate_nodes.get()
    if Y.bound > candidate_node.bound:
        candidate_nodes.pop()
        X = candidate_node
        if len(C_prime) > 2:
            candidate_nodes.add(Y)


# ===============================================
# Block 10: Do we have the best tour already?
# ===============================================

def block_10():
    global z_0
    if z_0 is not None and z_0 <= X.bound:
        return True
    else:
        return False


# ===============================================
# Block 11: Correct matrix for current vertex X
# ===============================================

def block_11():
    global C, C_prime

    # Is the next chosen vertex X the same as the curent vertex Y?
    if X == Y:
        # C_prime does not change, it's the same that we need
        return True

    # traversing the tree
    included_paths = []
    excluded_paths = []
    node = X

    while node.parent is not None:
        is_bar_vertex = node.path[0] < 0

        if is_bar_vertex:
            excluded_paths.append(node.path)
        else:
            included_paths.append(node.path)

        node = node.parent

    reset_C_prime()

    for path in excluded_paths:
        i_from = -path[0]
        j_to = -path[1]
        C_prime[row_map.index(i_from)][col_map.index(j_to)] = None

    cost_included_paths = 0

    for path in included_paths:
        i_from = path[0]
        j_to = path[1]

        cost_included_paths += C[ind(i_from)][ind(j_to)]

        delete_row_col(i_from, j_to)
        disable_path(j_to, i_from)

    C_prime, sum_subtrahends = simplify(C_prime)

    # adjust bound(X) value
    X.bound = cost_included_paths + sum_subtrahends

    return False


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

    # From the lecture exercises
    # 1 -> 2 -> 3 -> 5 -> 4 -> 1
    # Cost = 50
    C = [[0, 1, 21, 27, 5],
         [30, 0, 18, 23, 23],
         [27, 29, 0, 20, 10],
         [15, 2, 27, 0, 14],
         [28, 9, 15, 6, 0]]

    # From the book "Гудман С., Хидетниеми С. -
    # Введение в разработку и анализ алгоритмов", pp. 130
    # 1 -> 2 -> 3 -> 5 -> 4 -> 1
    # Cost = 62
    C = [[0, 25, 40, 31, 27],
         [5, 0, 17, 30, 25],
         [19, 15, 0, 6, 1],
         [9, 50, 24, 0, 6],
         [22, 8, 7, 10, 0]]

    C = [
        [0, 243, 57, 248, 144, 66, 120, 281, 61, 294, 171, 238, 307, 211, 242, 186, 49, 84, 101, 254],
        [243, 0, 296, 94, 208, 178, 125, 261, 234, 183, 66, 64, 236, 101, 265, 174, 287, 250, 202, 161],
        [57, 296, 0, 300, 171, 119, 172, 320, 88, 343, 224, 288, 349, 264, 269, 213, 58, 111, 128, 281],
        [248, 94, 300, 0, 161, 182, 134, 196, 238, 98, 97, 158, 151, 39, 200, 243, 297, 234, 231, 250],
        [144, 208, 171, 161, 0, 86, 114, 149, 83, 172, 158, 246, 178, 118, 98, 261, 193, 72, 186, 291],
        [66, 178, 119, 182, 86, 0, 54, 215, 56, 228, 106, 171, 241, 146, 184, 175, 115, 73, 101, 205],
        [120, 125, 172, 134, 114, 54, 0, 208, 110, 183, 59, 147, 234, 97, 193, 162, 168, 127, 130, 193],
        [281, 261, 320, 196, 149, 215, 208, 0, 233, 120, 239, 325, 75, 159, 53, 370, 329, 222, 310, 401],
        [61, 234, 88, 238, 83, 56, 110, 233, 0, 255, 162, 232, 262, 201, 181, 222, 110, 23, 137, 267],
        [294, 183, 343, 98, 172, 228, 183, 120, 255, 0, 165, 247, 55, 80, 153, 327, 342, 244, 299, 335],
        [171, 66, 224, 97, 158, 106, 59, 239, 162, 165, 0, 88, 219, 79, 224, 162, 220, 178, 136, 170],
        [238, 64, 288, 158, 246, 171, 147, 325, 232, 247, 88, 0, 300, 165, 312, 130, 243, 249, 159, 97],
        [307, 236, 349, 151, 178, 241, 234, 75, 262, 55, 219, 300, 0, 134, 124, 381, 355, 251, 336, 388],
        [211, 101, 264, 39, 118, 146, 97, 159, 201, 80, 79, 165, 134, 0, 157, 241, 260, 190, 213, 249],
        [242, 265, 269, 200, 98, 184, 193, 53, 181, 153, 224, 312, 124, 157, 0, 355, 291, 170, 284, 385],
        [186, 174, 213, 243, 261, 175, 162, 370, 222, 327, 162, 130, 381, 241, 355, 0, 169, 245, 85, 68],
        [49, 287, 58, 297, 193, 115, 168, 329, 110, 342, 220, 243, 355, 260, 291, 169, 0, 133, 84, 237],
        [84, 250, 111, 234, 72, 73, 127, 222, 23, 244, 178, 249, 251, 190, 170, 245, 133, 0, 161, 284],
        [101, 202, 128, 231, 186, 101, 130, 310, 137, 299, 136, 159, 336, 213, 284, 85, 84, 161, 0, 152],
        [254, 161, 281, 250, 291, 205, 193, 401, 267, 335, 170, 97, 388, 249, 385, 68, 237, 284, 152, 0]
    ]

    # ==============================================
    # Setting up variables
    # ==============================================

    # ================================
    # Matrix related
    # ================================
    C_prime = None

    row_map = []
    col_map = []

    i_from = None
    j_to = None
    max_Dij = None

    # ================================
    # Tree related
    # ================================
    X = None
    Y = None
    Y_bar = None
    candidate_nodes = CandidateNodes()

    # ================================
    # Tour related
    # ================================
    z_0 = None
    current_tour = []
    best_tour = []
    best_cost = -1

    # ================================
    # Iteration counter
    # ================================
    iterations = 1

    # ==============================================
    # Main loop
    # ==============================================

    if DEBUG:
        debug_block_1()
        debug_block_2()

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

            iterations += 1

    else:
        block_1()
        block_2()

        while True:
            block_3()
            block_4()
            block_5()

            if block_6():
                block_7()
                block_8()

            block_9()

            if not block_10():
                block_11()
            else:
                break

            iterations += 1

    print_solution()
