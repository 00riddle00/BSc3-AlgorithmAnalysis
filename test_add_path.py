#!/usr/bin/env python

import unittest

i_from = None
j_to = None
current_tour = []
possible_paths = []


def added_path_merge_on_i_from(s_index):
    global current_tour, j_to

    for s2_index, sublist_2 in enumerate(current_tour):
        if sublist_2[0] == j_to:
            current_tour[s_index] = current_tour[s_index] + sublist_2[1:]
            del (current_tour[s2_index])
            return True
    return False


def added_path_merge_on_j_to(s_index):
    global current_tour, i_from

    for s2_index, sublist_2 in enumerate(current_tour):
        if sublist_2[-1] == i_from:
            current_tour[s_index] = sublist_2[:-1] + current_tour[s_index]
            del (current_tour[s2_index])
            return True
    return False


def add_path_already_have_i_from(s_index, sublist):
    global current_tour, j_to

    if sublist[0] == j_to:
        return False
    else:
        current_tour[s_index].append(j_to)

        if added_path_merge_on_i_from(s_index):
            return True

        return True


def add_path_already_have_j_to(s_index, sublist):
    global current_tour, i_from

    if sublist[-1] == i_from:
        return False
    else:
        current_tour[s_index].insert(0, i_from)

        if added_path_merge_on_j_to(s_index):
            return True

        return True


def try_add_this_path():
    global current_tour, i_from, j_to

    for s_index, sublist in enumerate(current_tour):
        if i_from == sublist[-1]:
            return add_path_already_have_i_from(s_index, sublist)
        elif j_to == sublist[0]:
            return add_path_already_have_j_to(s_index, sublist)

    current_tour.append([i_from, j_to])
    return True


def add_path():
    #global i_from, j_to
    global possible_paths, i_from, j_to

    for path in possible_paths:
        i_from = path[0]
        j_to = path[1]

        if try_add_this_path():
            #return True
            return current_tour

    return False


class TestDraft(unittest.TestCase):

    def test_cases(self):
        global possible_paths, current_tour

        possible_paths = [[1, 2]]
        current_tour = []
        result = [[1, 2]]
        self.assertEqual(add_path(), result)

        possible_paths = [[5, 1]]
        current_tour = [[1, 2]]
        result = [[5, 1, 2]]
        self.assertEqual(add_path(), result)

        possible_paths = [[3, 5]]
        current_tour = [[5, 1, 2]]
        result = [[3, 5, 1, 2]]
        self.assertEqual(add_path(), result)

        possible_paths = [[4, 8]]
        current_tour = [[3, 5, 1, 2]]
        result = [[3, 5, 1, 2], [4, 8]]
        self.assertEqual(add_path(), result)

        possible_paths = [[8, 3], [8, 6]]
        current_tour = [[3, 5, 1, 2], [4, 8]]
        result = [[4, 8, 3, 5, 1, 2]]
        self.assertEqual(add_path(), result)

        possible_paths = [[7, 8], [3, 4]]
        current_tour = [[4, 6, 2], [1, 5, 3]]
        result = [[4, 6, 2], [1, 5, 3], [7, 8]]
        self.assertEqual(add_path(), result)

        possible_paths = [[4, 8], [4, 6]]
        current_tour = [[8, 3, 5], [2, 4], [6, 1]]
        result = [[2, 4, 8, 3, 5], [6, 1]]
        self.assertEqual(add_path(), result)

        possible_paths = [[7, 8], [1, 9]]
        current_tour = [[4, 6, 2], [8, 5, 3]]
        result = [[4, 6, 2], [7, 8, 5, 3]]
        self.assertEqual(add_path(), result)

        possible_paths = [[8, 5], [1, 9]]
        current_tour = [[5, 3, 6, 7], [1, 2, 4], [9, 8]]
        result = [[9, 8, 5, 3, 6, 7], [1, 2, 4]]
        self.assertEqual(add_path(), result)

        possible_paths = [[8, 5], [1, 9]]
        current_tour = [[3, 6, 8], [2, 1], [5, 7, 4]]
        result = [[3, 6, 8, 5, 7, 4], [2, 1]]
        self.assertEqual(add_path(), result)

        possible_paths = [[8, 2]]
        current_tour = [[3, 6, 8], [2, 1]]
        result = [[3, 6, 8, 2, 1]]
        self.assertEqual(add_path(), result)

        possible_paths = [[3, 5], [4, 6]]
        current_tour = [[5, 1, 3]]
        result = [[5, 1, 3], [4, 6]]
        self.assertEqual(add_path(), result)

        possible_paths = [[2, 4]]
        current_tour = [[5, 1, 3], [4, 6]]
        result = [[5, 1, 3], [2, 4, 6]]
        self.assertEqual(add_path(), result)

        possible_paths = [[2, 4], [3, 1], [3, 4]]
        current_tour = [[1, 3], [4, 2]]
        result = [[1, 3, 4, 2]]
        self.assertEqual(add_path(), result)


if __name__ == '__main__':
    unittest.main()
