import numpy as np


def create_solution_matrix(dictionary):
    min_index_row = min(list(zip(*dictionary.keys()))[0])
    max_index_row = max(list(zip(*dictionary.keys()))[0])
    min_index_col = min(list(zip(*dictionary.keys()))[1])
    max_index_col = max(list(zip(*dictionary.keys()))[1])

    number_of_rows = max_index_row - min_index_row + 1
    number_of_columns = max_index_col - min_index_col + 1

    matrix = np.zeros((number_of_rows, number_of_columns))

    for i in range(number_of_rows):
        for j in range(number_of_columns):
            key = (i + min_index_row, j + min_index_col)
            matrix[i, j] = dictionary[key].X
    return matrix


def create_binary_solution_matrix(dictionary):
    min_index_row = min(list(zip(*dictionary.keys()))[0])
    max_index_row = max(list(zip(*dictionary.keys()))[0])
    min_index_col = min(list(zip(*dictionary.keys()))[1])
    max_index_col = max(list(zip(*dictionary.keys()))[1])

    number_of_rows = max_index_row - min_index_row + 1
    number_of_columns = max_index_col - min_index_col + 1

    matrix = np.zeros((number_of_rows, number_of_columns))

    for i in range(number_of_rows):
        for j in range(number_of_columns):
            key = (i+min_index_row, j+min_index_col)
            if dictionary[key].X > 0.1: matrix[i, j] = 1
            else: matrix[i, j] = 0
    return matrix

def create_binary_solution_vector(dictionary):
    min_index = min(dictionary.keys())
    vector = np.zeros(len(dictionary))
    for i in range(len(dictionary)):
        key = min_index + i
        if dictionary[key].X > 0.1:
            vector[i] = 1
        else:
            vector[i] = 1
    return vector

def create_solution_dict(dict_gurobi):
    dict_result = {}
    for key in dict_gurobi.keys():
        dict_result[key] = dict_gurobi[key].X
    return dict_result

def create_binary_solution_dict(dict_gurobi):
    dict_result = {}
    for key in dict_gurobi.keys():
        if dict_gurobi[key].X > 0.1:
            dict_result[key] = 1
        else:
            dict_result[key] = 0
    return dict_result
