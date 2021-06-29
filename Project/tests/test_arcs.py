#!/usr/bin/env python

import random


def print_M(matrix_name, M):
    print(f'{matrix_name} = ')
    for row in M:
        print('    ', row)
    print('\n')


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


if __name__ == '__main__':
    random.seed(0)

    # all zeroes except 10 elements such that every
    # row and every column have exactly one element
    M_1 = generate_new_matrix(10, [1, 10], arcs=10)
    assert (M_1 == [[0, 0, 0, 0, 0, 8, 0, 0, 0, 0],
                    [0, 0, 0, 0, 5, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
                    [0, 6, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
                    [0, 0, 0, 0, 0, 0, 0, 8, 0, 0],
                    [0, 0, 8, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 8, 0, 0, 0],
                    [0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    # 5 zeroes not in the main diagonal
    M_2 = generate_new_matrix(10, [1, 10], arcs=85)
    assert (M_2 == [[0, 1, 3, 3, 6, 9, 5, 2, 10, 8],
                    [3, 0, 8, 7, 10, 9, 5, 6, 0, 5],
                    [3, 9, 0, 8, 2, 0, 1, 9, 5, 3],
                    [4, 8, 6, 0, 5, 6, 10, 10, 3, 5],
                    [7, 7, 2, 1, 0, 4, 6, 0, 4, 4],
                    [8, 7, 10, 7, 1, 0, 0, 7, 1, 3],
                    [8, 2, 5, 3, 8, 9, 0, 9, 10, 1],
                    [1, 8, 6, 5, 8, 1, 7, 0, 9, 2],
                    [3, 1, 0, 7, 6, 1, 4, 1, 0, 9],
                    [10, 2, 4, 2, 10, 4, 5, 5, 3, 0]])

    # 50 zeroes not in the main diagonal
    M_3 = generate_new_matrix(10, [1, 10], arcs=40)
    assert (M_3 == [[0, 0, 1, 4, 5, 0, 0, 0, 0, 0],
                    [10, 0, 0, 7, 6, 0, 0, 4, 0, 0],
                    [5, 0, 0, 3, 0, 0, 6, 6, 0, 0],
                    [10, 1, 1, 0, 0, 0, 10, 0, 0, 0],
                    [0, 3, 0, 0, 0, 0, 0, 5, 3, 9],
                    [0, 5, 7, 0, 5, 0, 0, 0, 0, 8],
                    [8, 6, 0, 0, 0, 0, 0, 0, 1, 5],
                    [0, 0, 3, 10, 7, 2, 0, 0, 0, 0],
                    [1, 0, 0, 2, 0, 0, 0, 5, 0, 8],
                    [0, 4, 7, 0, 0, 4, 5, 0, 3, 0]])
