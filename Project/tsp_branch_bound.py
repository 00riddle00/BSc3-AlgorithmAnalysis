#!/usr/bin/env python3
import argparse
import random
import sys
import time

# ==============================================================
# Declare global variables
# ==============================================================

# Verbose (DEBUG) mode
global DEBUG
# Matrix related
global C, C_prime, row_map, col_map, i_from, j_to, max_Dij
# Tree related
global X, Y, Y_bar, candidate_nodes
# Tour related
global current_tour, best_tour, best_cost, names
# Iteration counter
global iterations


# ==============================================================
# DEBUG printing functions
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
    global iterations

    if DEBUG:
        print('=========================')
        print(f'Block {block_no} (iteration {iterations})')
        print('=========================\n')


# ==============================================================
# Functions checking for correctness
# ==============================================================
def check_tour(tour, check_len=True, flatten=False):
    global C

    if flatten:
        tour = [city for sublist in tour for city in sublist]
    if check_len:
        assert len(tour) == len(C), \
            'The tour is shorter than the number of cities'

    assert len(tour) == len(set(tour)), \
        'There are repeated vertices in the current tour'


# ==============================================================
# Utility classes
# ==============================================================

# Binary tree node
class Node:

    def __init__(self, parent, path, bound=None):
        self.parent = parent
        self.path = path
        self.left_child = None
        self.right_child = None
        self.bound = bound


# Priority queue
class CandidateNodes:

    def __init__(self):
        self.nodelist = []
        self.size = 0

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
        node = self.nodelist[0]
        self.nodelist = self.nodelist[1:]
        self.size -= 1
        return node


# ==============================================================
# Utility functions
# ==============================================================

# --------------------------------------------------
# Utility functions which do not use main
# program variables
# --------------------------------------------------

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
    row_no_none = [x for x in row if (x is not None)]
    if row_no_none:
        return min(row_no_none)
    else:
        return 0


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


def find_max_Dij(M):
    _max_Dij = 0
    paths = []

    M_T = transpose(M)

    for i, row in enumerate(M, 1):
        for j, el in enumerate(row, 1):
            if el == 0:
                # i-th row and j-th column element is zero
                # hence there is no path i -> j, meaning there are
                # such paths 1 -> k and l -> 2 where k != 2 and l != 1.
                #
                # For every such path their bound will increase by
                # the size D[i,j] =
                #   min(i-th row without j-th element) +
                #   min(j-th column without i-th element)
                D_ij = \
                    min_no_element(M[ind(i)], ind(j)) + \
                    min_no_element(M_T[ind(j)], ind(i))

                if D_ij == _max_Dij:
                    paths.append([row_map[ind(i)], col_map[ind(j)]])
                elif D_ij > _max_Dij:
                    _max_Dij = D_ij
                    paths = [[row_map[ind(i)], col_map[ind(j)]]]

    return paths, _max_Dij


# --------------------------------------------------
# Utilify functions which use main program variables
# --------------------------------------------------

def print_names():
    global best_tour, names

    if names:
        for v in best_tour:
            print(f'{names[v]} ->', end=' ')
        print(f'{names[best_tour[0]]}\n')


def print_solution():
    global best_tour, best_cost

    print('=========================')
    print(f'Solution (size = {len(C)})')
    print('=========================\n')
    for v in best_tour:
        print(f'{v} ->', end=' ')
    print(best_tour[0])
    print(f'\nCost = {best_cost}\n')
    print_names()


# --------------------------------------------------
# Utility functions which use and change main
# program variables
# --------------------------------------------------

# -----------------------------
# Generate new matrix
# -----------------------------
def generate_new_matrix(cities, weights, arcs=None):
    M = []
    rows = cities
    cols = cities

    for i in range(rows):
        row = [random.randrange(weights[0], weights[1] + 1) for _ in range(cols)]
        row[i] = 0  # main diagonal element
        M.append(row)

    if arcs:
        max_arcs_no = rows * (rows - 1)

        non_removable_arcs = []
        col_numbers = [j for j in range(cols)]
        for i in range(rows):
            col_numbers_except_main_diagonal = [(col_numbers_index, j) for col_numbers_index, j in
                                                enumerate(col_numbers) if j != i]
            tmp = col_numbers_except_main_diagonal[random.choice(range(len(col_numbers_except_main_diagonal)))]
            col_numbers_index = tmp[0]
            j = tmp[1]
            non_removable_arcs.append([i, j])
            col_numbers = col_numbers[:col_numbers_index] + col_numbers[col_numbers_index + 1:]

        removable_arcs = []

        for i in range(rows):
            for j in range(cols):
                if i != j and [i, j] not in non_removable_arcs:
                    removable_arcs.append([i, j])

        removed_arcs_no = max_arcs_no - arcs

        for _ in range(removed_arcs_no):
            removed_arc_index = random.choice(range(len(removable_arcs)))
            i_j = removable_arcs[removed_arc_index]
            i = i_j[0]
            j = i_j[1]
            M[i][j] = 0
            removable_arcs = removable_arcs[:removed_arc_index] + removable_arcs[removed_arc_index + 1:]

    return M


# -----------------------------
# For matrix operations
# -----------------------------
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
    C_prime = \
        C_prime[:row_map.index(i_row)] + C_prime[(row_map.index(i_row) + 1):]

    # delete j-th column
    C_prime_T = transpose(C_prime)
    C_prime_T = \
        C_prime_T[:col_map.index(j_col)] + \
        C_prime_T[(col_map.index(j_col) + 1):]
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


# -----------------------------
# For adding a new path
# -----------------------------
def added_path_merge_on_i_from(s_index):
    global j_to
    global current_tour

    for s2_index, sublist_2 in enumerate(current_tour):
        if sublist_2[0] == j_to:
            current_tour[s_index] = current_tour[s_index] + sublist_2[1:]
            del (current_tour[s2_index])
            return True
    return False


def added_path_merge_on_j_to(s_index):
    global i_from
    global current_tour

    for s2_index, sublist_2 in enumerate(current_tour):
        if sublist_2[-1] == i_from:
            current_tour[s_index] = sublist_2[:-1] + current_tour[s_index]
            del (current_tour[s2_index])
            return True
    return False


def add_path_already_have_i_from(s_index, sublist):
    global j_to
    global current_tour

    if sublist[0] == j_to:
        return False
    else:
        current_tour[s_index].append(j_to)

        if added_path_merge_on_i_from(s_index):
            return True

        return True


def add_path_already_have_j_to(s_index, sublist):
    global i_from
    global current_tour

    if sublist[-1] == i_from:
        return False
    else:
        current_tour[s_index].insert(0, i_from)

        if added_path_merge_on_j_to(s_index):
            return True

        return True


def try_add_this_path():
    global i_from, j_to
    global current_tour

    for s_index, sublist in enumerate(current_tour):
        if i_from == sublist[-1]:
            return add_path_already_have_i_from(s_index, sublist)
        elif j_to == sublist[0]:
            return add_path_already_have_j_to(s_index, sublist)

    current_tour.append([i_from, j_to])
    return True


def add_path(possible_paths):
    global i_from, j_to

    for path in possible_paths:
        i_from = path[0]
        j_to = path[1]

        if try_add_this_path():
            return True

    return False


# ==============================================================
# Main program functions: blocks wrapped in DEBUG mode
# ==============================================================

def debug_block_1():
    global C

    debug_block_name(1)
    block_1()
    debug('Input (distance matrix):\n')
    debug_M('C', C)


def debug_block_2():
    global C_prime
    global X

    debug_block_name(2)
    block_2()
    debug(f'Bound(Root) = {X.bound}\n')
    debug_M('C_prime', C_prime)


def debug_block_3():
    global i_from, j_to, max_Dij
    global Y, Y_bar

    debug_block_name(3)
    new_path_added = block_3()
    debug(f'Child vertices: '
          f'Y_bar = ("{Y_bar.path[0]},{Y_bar.path[1]}"), '
          f'Y = ("{Y.path[0]},{Y.path[1]}")')
    debug(f'from: i = {i_from}, to: j = {j_to}')
    debug(f'max_Dij = {max_Dij}\n')
    if new_path_added:
        return True
    else:
        return False


def debug_block_4():
    global i_from, j_to
    global Y_bar

    debug_block_name(4)
    block_4()
    debug(f'Bound("({-i_from},{-j_to})") = {Y_bar.bound}\n')


def debug_block_5():
    global C_prime, i_from, j_to
    global Y

    debug_block_name(5)
    block_5()
    debug(f'Bound("({i_from},{j_to})") = {Y.bound}\n')
    debug_M('C_prime', C_prime)


def debug_block_6():
    global C_prime

    debug_block_name(6)
    is_matrix_2x2 = block_6()
    size = len(C_prime)

    if is_matrix_2x2:
        debug(f'Matrix is simple enough (size = {size}x{size})\n')
    else:
        debug(f'Matrix is not simple enough (size = {size}x{size})\n')

    return is_matrix_2x2


def debug_block_7():
    global Y
    global current_tour

    debug_block_name(7)
    block_7()
    debug(f'Current tour: {current_tour}')
    debug(f'Bound("Y_last") = {Y.bound} ( = cost of this tour)\n')


def debug_block_8():
    global best_tour, best_cost

    debug_block_name(8)
    old_best_cost = best_cost

    block_8()

    if best_cost != old_best_cost:
        debug(f'Better tour has been found: {best_tour}\n')
    else:
        debug(
            f'We did not find a better tour. Best tour so far: {best_tour}\n')


def debug_block_9():
    global X

    debug_block_name(9)
    block_9()
    i, j = X.path[0], X.path[1]
    debug(f'Next vertex: X = ("{i},{j}")')
    debug(f'Bound("({i},{j})") = {X.bound}\n')


def debug_block_10():
    global X
    global best_tour, best_cost

    debug_block_name(10)
    is_no_better_path = block_10()

    if is_no_better_path:
        debug('The next chosen vertex does not contain the better tour '
              'than we already have. The algorithm stops here.\n')
    else:
        best_tour_bound = 'infinity'
        if len(best_tour):
            best_tour_bound = f'{best_cost}'

        debug(f'The next chosen vertex has a smaller lower bound '
              f'(bound >= {X.bound}) than the cost of the current '
              f'best tour (cost = {best_tour_bound}).')
        debug('Hence the algorithm proceeds.\n')

    return is_no_better_path


def debug_block_11():
    global C_prime
    global X

    debug_block_name(11)
    is_vertex_the_same = block_11()

    if is_vertex_the_same:
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
# Main program functions: blocks
# ==============================================================

# --------------------------------------------------
# Block 1: Input data
# --------------------------------------------------

def block_1():
    global C

    # convert 0s to None, meaning INF
    C_tmp = []
    for row in C:
        C_tmp.append([None if x == 0 else x for x in row])

    C = C_tmp


# --------------------------------------------------
# Block 2: Matrix simplification and finding the
#          bound of the root vertex
# --------------------------------------------------

def block_2():
    global C, C_prime, row_map, col_map
    global X

    reset_C_prime()
    C_prime, bound_root = simplify(C_prime)
    X = Node(None, (None, None), bound=bound_root)


# --------------------------------------------------
# Block 3: Choosing the next vertex "(i,j)" for
#          branching
# --------------------------------------------------

def block_3():
    global C_prime, i_from, j_to, max_Dij
    global X, Y, Y_bar
    global current_tour

    # reset these global variables
    i_from = None
    j_to = None
    max_Dij = None

    # calculate the change of bound for all
    # elements in the matrix whose value is 0
    possible_paths, max_Dij = find_max_Dij(C_prime)

    if not possible_paths:
        return False

    i_from = possible_paths[0][0]
    j_to = possible_paths[0][1]

    if not current_tour:
        current_tour.append([i_from, j_to])
    else:
        while not add_path(possible_paths):
            C_prime[row_map.index(i_from)][col_map.index(j_to)] = None
            possible_paths, max_Dij = find_max_Dij(C_prime)

            if not possible_paths:
                return False

            i_from = possible_paths[0][0]
            j_to = possible_paths[0][1]

    check_tour(current_tour, check_len=False, flatten=True)

    Y_bar = Node(X, (-i_from, -j_to))
    Y = Node(X, (i_from, j_to))

    X.left_child = Y_bar
    X.right_child = Y

    return True


# --------------------------------------------------
# Block 4: Branching - finding the bound of the
#          vertex "(i,j)_bar"
# --------------------------------------------------

def block_4():
    global max_Dij
    global X, Y_bar
    global candidate_nodes

    Y_bar.bound = X.bound + max_Dij
    # we always check Y first, so let's save
    # Y_bar for later
    candidate_nodes.add(Y_bar)


# --------------------------------------------------
# Block 5: Branching - finding the bound of
#          the vertex "(i,j)"
# --------------------------------------------------

def block_5():
    global C_prime, i_from, j_to
    global X, Y

    delete_row_col(i_from, j_to)
    disable_path(j_to, i_from)
    C_prime, sum_subtrahends = simplify(C_prime)

    Y.bound = X.bound + sum_subtrahends

    # reset X
    X = None


# --------------------------------------------------
# Block 6: Is the distance matrix small enough?
# --------------------------------------------------

# check matrix dimensions
def block_6():
    global C_prime
    return len(C_prime) == 2


# --------------------------------------------------
# Block 7: Exhaustive estimation of the remaining
#          matrix
# --------------------------------------------------

def block_7():
    global C, row_map, col_map
    global Y
    global current_tour

    cost = 0

    if len(current_tour) == 2:
        paths = current_tour[0] + current_tour[1]
    elif len(current_tour) == 1:
        possible_paths_pair_1 = [[row_map[0], col_map[0]],
                                 [row_map[1], col_map[1]]]

        possible_paths_pair_2 = [[row_map[0], col_map[1]],
                                 [row_map[1], col_map[0]]]

        current = current_tour.copy()

        path_added = add_path(possible_paths_pair_1)

        if not path_added or len(current_tour) > 1:
            current_tour = current

            path_added = add_path(possible_paths_pair_2)

            if not path_added:
                raise Exception(
                    f'Something went wrong, no path was not added '
                    f'at the last stage, when matrix size is 2x2\n')

        paths = current_tour[0]
    else:
        raise Exception(
            f'Something went wrong, there should only be 1 or 2 sublists'
            f' at the end when matrix size is 2x2, got {len(current_tour)}')

    check_tour(paths)

    for i in range(len(paths[:-1])):
        cost += C[ind(paths[i])][ind(paths[i + 1])]
    cost += C[ind(paths[-1])][ind(paths[0])]

    current_tour = paths
    Y.bound = cost


# --------------------------------------------------
# Block 8: Is bound_Y_last < best_cost? If yes, save
#          the current tour as the best so far
# --------------------------------------------------

def block_8():
    global Y
    global current_tour, best_tour, best_cost

    cost = Y.bound
    if best_cost is None or cost < best_cost:
        best_cost = cost
        best_tour = current_tour


# --------------------------------------------------
# Block 9: Choose the next vertex
# --------------------------------------------------

def block_9():
    global C_prime
    global X, Y
    global candidate_nodes

    X = Y

    if Y.bound > candidate_nodes.get().bound:
        X = candidate_nodes.pop()
        if len(C_prime) > 2:
            candidate_nodes.add(Y)


# --------------------------------------------------
# Block 10: Do we have the best tour already?
# --------------------------------------------------

def block_10():
    global X
    global best_tour, best_cost

    if best_cost is not None and best_cost <= X.bound:
        # make the tour start from city no. 1
        index_of_1 = best_tour.index(1)
        best_tour = best_tour[index_of_1:] + best_tour[:index_of_1]
        return True
    else:
        return False


# --------------------------------------------------
# Block 11: Correct matrix for current vertex X
# --------------------------------------------------

def block_11():
    global C, C_prime, row_map, col_map, i_from, j_to
    global X, Y
    global current_tour

    # Is the next chosen vertex X the same as
    # the curent vertex Y?
    if X == Y:
        # C_prime does not change, it's the same
        # that we need
        return True

    # reset these global variables
    reset_C_prime()
    current_tour = []

    # traversing the tree
    node = X
    cost_included_paths = 0

    while node.parent is not None:

        i_from = node.path[0]
        j_to = node.path[1]

        if i_from < 0 and j_to < 0:
            if -i_from in row_map and -j_to in col_map:
                C_prime[row_map.index(-i_from)][col_map.index(-j_to)] = None
        else:
            if not current_tour:
                current_tour.append([i_from, j_to])
            else:
                path_added = add_path([[node.path[0], node.path[1]]])
                if not path_added:
                    raise Exception(
                        f'Something went wrong, no path was added\n')

            cost_included_paths += C[ind(i_from)][ind(j_to)]

            delete_row_col(i_from, j_to)
            disable_path(j_to, i_from)

        node = node.parent

    C_prime, sum_subtrahends = simplify(C_prime)

    # adjust bound(X) value
    X.bound = cost_included_paths + sum_subtrahends

    return False


# ==============================================================
# Main program: code
# ==============================================================
if __name__ == '__main__':
    # --------------------------------------------------
    # Initialize global variables (part 1/2)
    # --------------------------------------------------

    DEBUG = False
    C = []
    names = {}

    # --------------------------------------------------
    # Parse arguments
    # --------------------------------------------------
    parser = argparse.ArgumentParser(
        description='### This program solves travelling salesman problem '
                    '(TSP) using branch and bound algorithm ###',
        usage='\n    tsp_branch_bound.py input_file [-o OUTPUT_FILE] [-d/-s]\n'
              '\nusage for randomized input:'
              '\n    tsp_branch_bound.py -c CITIES [-a ARCS] [-w MIN MAX] '
              '[-r RANDOM_SEED] [-o OUTPUT_FILE] [-d/-s]\n'
              '\nusage for executing many test runs:'
              '\n    tsp_branch_bound.py -c CITIES [-a ARCS] [-w MIN MAX] '
              '[-r RANDOM_SEED] [-o OUTPUT_FILE] [-t TEST_RUNS] [-s]\n'
              '\nTry tsp_branch_bound.py --help for more information.')

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='run in explicit (visual) debug '
                             'mode, with every step annotated')

    parser.add_argument('input_file',
                        nargs='?',
                        help='a file to get input from')

    parser.add_argument('-c', '--cities',
                        type=int,
                        help='[randomize input]: number of cities '
                             '(vertices). Minimum value is 3')

    parser.add_argument('-a', '--arcs',
                        type=int,
                        help='[randomize input]: number of arcs (paths). '
                             'Minimum value is c, maximum - c*(c-1), where c '
                             'is the specified number of cities (vertices). '
                             'Default value is the maximum: c*(c-1)')

    parser.add_argument('-w', '--weights',
                        nargs=2,
                        type=int,
                        metavar=('MIN', 'MAX'),
                        help='[randomize input]: minimum and maximum '
                             'values of weights. Minimum value is 1. '
                             'Default interval: 1 10')

    parser.add_argument('-r', '--random_seed',
                        type=int,
                        help='[randomize input]: set random seed for '
                             'possible repetition. Default value: 0')

    parser.add_argument('-o', '--output_file',
                        help='a file to write output to')

    parser.add_argument('-t', '--test_runs',
                        type=int,
                        help='execute the indicated amount of test runs. '
                             'The solution will not be printed, average times'
                             'and number of iterations will be shown instead')

    parser.add_argument('-s', '--silent',
                        action='store_true',
                        help='set non-verbose output '
                             '(prints only time passed in seconds)')

    args = parser.parse_args()

    DEBUG = args.debug
    arg_count = len(sys.argv)

    if arg_count == 1 or args.debug and arg_count == 2:
        parser.print_usage()
        sys.exit()

    INPUT_FILE = args.input_file

    if INPUT_FILE:
        if args.cities:
            print("tsp_branch_bound.py: error: argument -c/--cities: "
                  "can not be used when input file is specified")
            sys.exit()
        elif args.weights:
            print("tsp_branch_bound.py: error: argument -w/--weights: "
                  "can not be used when input file is specified")
            sys.exit()
        elif args.random_seed:
            print("tsp_branch_bound.py: error: argument -r/--random_seed: "
                  "can not be used when input file is specified")
        elif args.test_runs:
            print("tsp_branch_bound.py: error: argument -t/--test_runs: "
                  "can not be used when input file is specified")
        elif args.arcs:
            print("tsp_branch_bound.py: error: argument -a/--arcs: "
                  "can not be used when input file is specified")
            sys.exit()
    else:
        if not args.cities:
            print("tsp_branch_bound.py: error: argument -c/--cities: "
                  "this argument is required, if no input file is specified")
            sys.exit()
        elif args.cities < 0:
            print("tsp_branch_bound.py: error: argument -c/--cities: "
                  "the number cannot be negative")
            sys.exit()
        elif args.cities < 3:
            print("tsp_branch_bound.py: error: argument -c/--cities: "
                  "the minimum number is 3")
            sys.exit()

        if args.weights:
            if args.weights[0] < 1 or args.weights[1] < 1:
                print("tsp_branch_bound.py: error: argument -w/--weights:"
                      " Minimum weight value is 1")
                sys.exit()
            elif args.weights[1] < args.weights[0]:
                print("tsp_branch_bound.py: error: argument -w/--weights:"
                      " incorrect weights interval")
                sys.exit()

        if args.arcs:
            if args.arcs < args.cities or args.arcs > (args.cities * (args.cities - 1)):
                print(f"tsp_branch_bound.py: error: argument -a/--arcs: "
                      f"Minimum value: {args.cities}, maximum: {args.cities * (args.cities - 1)}. "
                      f"These values depend on the specified number of cities")
                sys.exit()

    if args.debug:
        if args.silent:
            print("tsp_branch_bound.py: error: argument -s/--silent: "
                  "can not be used with debug mode")
            sys.exit()
        elif args.test_runs:
            print("tsp_branch_bound.py: error: argument -t/--test_runs: "
                  "can not be used with debug mode")
            sys.exit()

    if args.output_file:
        sys.stdout = open(args.output_file, 'a')

    random_seed = 1

    if not args.input_file:
        if args.random_seed:
            random_seed = args.random_seed
        random.seed(random_seed)

        cities = args.cities
        w_1 = 1
        w_n = 10
        if args.weights:
            w_1 = args.weights[0]
            w_n = args.weights[1]

        weights = [w_1, w_n]
        C = generate_new_matrix(cities, weights, args.arcs)

    else:
        # --------------------------------------------------
        # Read input file
        # --------------------------------------------------

        # Square distance matrix 'C' (between points),
        # which is read from the input file:
        #
        #              columns:
        # rows:     1    2   ...  n
        #   1     (a_11 a_12 ... a_1n)
        #   2     (a_21 a_22 ... a_2n)
        #  ...
        #   n     (an_1 an_2 ... a_nn)
        #
        # see input.example.txt file for input format
        with open(args.input_file) as input_file:

            lines = []
            matrix_size = 0

            for line in input_file.readlines():
                if line != '\n' and not line.startswith('#'):
                    lines.append(line.split())

            # this fixes a weird bug with trailing
            # newlines in the input file
            for line in lines:
                pass

            if lines[0][0] == '@names':
                for i, line in enumerate(lines[1:], 1):
                    if line[0] == '\n' or line[0].startswith('['):
                        if not matrix_size:
                            matrix_size = i - 1
                        elif matrix_size != i - 1:
                            raise ValueError(
                                f'there should be a total of {matrix_size} '
                                f'names, got {i - 1} instead')
                        break
                    else:
                        names[i] = line[0]

                lines = lines[matrix_size + 1:]

            if lines[0][0].startswith('['):
                if not matrix_size:
                    matrix_size = len(lines[0][1:-1])
                for i, row in enumerate(lines, 1):
                    if line[0] == '\n' or line[0].startswith('@'):
                        break
                    elif len(row[1:-1]) == matrix_size:
                        C.append([int(el) for el in row[1:-1]])
                    else:
                        raise ValueError(
                            f'matrix at row {i} should have {matrix_size} '
                            f'columns, got {len(row[1:-1])} instead\n'
                            f'(this error might mean that there may be some'
                            f' additional problems in the input file)')

                lines = lines[matrix_size:]

    # --------------------------------------------------
    # Initialize global variables (part 2/2)
    # --------------------------------------------------

    # DEBUG - already initialized in (part 1/2)
    #         and then defined by -d flag

    # -----------------------------
    # Matrix related
    # -----------------------------
    # C - already initialized in (part 1/2) and then defined
    #     either from input file or by randomly generating it
    C_prime = None

    row_map = []
    col_map = []

    i_from = None
    j_to = None
    max_Dij = None

    # -----------------------------
    # Tree related
    # -----------------------------
    X = None
    Y = None
    Y_bar = None
    candidate_nodes = CandidateNodes()

    # -----------------------------
    # Tour related
    # -----------------------------
    current_tour = []
    best_tour = []
    best_cost = None
    # names - already initialized in (part 1/2) and then
    #         either defined from input file or left empty

    # -----------------------------
    # Iteration counter
    # -----------------------------
    iterations = 0

    # --------------------------------------------------
    # Main loop (DEBUG mode)
    # --------------------------------------------------

    if DEBUG:
        start_time = time.time()

        debug_block_1()
        debug_block_2()

        while True:
            iterations += 1
            if not debug_block_3():
                Y = candidate_nodes.pop()
                X = candidate_nodes.pop()
                debug_block_11()
                continue

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

        end_time = time.time()

        check_tour(best_tour)
        print_solution()
        print(f'--------- {iterations} iterations -----------')
        print(f'--- {end_time - start_time} seconds ---')
        print(60 * '-')

    # --------------------------------------------------
    # Main loop (standard mode)
    # --------------------------------------------------
    elif not args.test_runs:
        start_time = time.time()

        block_1()
        block_2()

        while True:
            iterations += 1
            if not block_3():
                Y = candidate_nodes.pop()
                X = candidate_nodes.pop()
                block_11()
                continue

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

        end_time = time.time()

        if args.silent:
            print(end_time - start_time)
        else:
            check_tour(best_tour)
            print_solution()
            print(f'--------- {iterations} iterations -----------')
            print(f'--- {end_time - start_time} seconds ---')
            print(60 * '-')

    # --------------------------------------------------
    # Main loop (testing mode)
    # --------------------------------------------------
    else:
        total_time = 0
        total_time_per_iteration = 0
        total_iterations = 0

        for test_run in range(1, args.test_runs + 1):

            start_time = time.time()

            block_1()
            block_2()

            while True:
                iterations += 1
                if not block_3():
                    Y = candidate_nodes.pop()
                    X = candidate_nodes.pop()
                    block_11()
                    continue

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

            end_time = time.time()

            time_taken = end_time - start_time
            time_per_iteration = time_taken / iterations

            total_time += time_taken
            total_time_per_iteration += time_per_iteration
            total_iterations += iterations

            # --------------------------------------------------
            # Create new input matrix with different
            # random seed for each new test run
            # --------------------------------------------------

            random.seed(random_seed + test_run)
            C = generate_new_matrix(args.cities, weights, args.arcs)

            # --------------------------------------------------
            # Reinitialize global variables
            # --------------------------------------------------
            C_prime = None

            row_map = []
            col_map = []

            i_from = None
            j_to = None
            max_Dij = None

            X = None
            Y = None
            Y_bar = None
            candidate_nodes = CandidateNodes()

            current_tour = []
            best_tour = []
            best_cost = None

            iterations = 0

        avg_time = total_time / args.test_runs
        avg_time_per_iteration = total_time_per_iteration / args.test_runs
        avg_iterations = total_iterations / args.test_runs

        if args.silent:
            print(f'{avg_time}, {avg_time_per_iteration}, {avg_iterations}')
        else:
            print('-------------------------------------------------')
            print(f'Vertices (cities): {args.cities}\n'
                  # todo change to user specified
                  f'Arcs (paths): {args.cities * (args.cities - 1)}\n'
                  f'Possible smallest path length (w_1): {w_1}\n'
                  f'Possible largest path length (w_n): {w_n}\n')
            print(f'Total time (avg): {avg_time}s\n'
                  f'Time per iteration (avg): {avg_time_per_iteration}s\n'
                  f'Iterations in one test run (avg): {avg_iterations}\n'
                  f'Total number of test runs: {args.test_runs}\n'
                  f'Random seeds of the test runs (interval): '
                  f'{args.random_seed}-{args.random_seed + args.test_runs - 1}')
            print('-------------------------------------------------')
