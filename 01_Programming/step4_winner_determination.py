import numpy as np
import gurobipy as gp
from gurobipy import GRB
import os
from Input.file_management import read_files
from Post_Processing.gurobi_post_process import create_binary_solution_dict

def create_B_bi(df_bidding):
    """
    creates the bidding matrix for the linear model
    :param df_bidding:
    :return: dictionary B_id, in which bidder i, reported bid b
    """
    B_bi = {}
    for row in df_bidding.iterrows():
        if row[1]['bundle_id'] >= 0:   #exclude initial bundles, which have an index of -1 or -2
            bid = row[1]['marginal_costs']
            i = int(row[1]['unique_machine_id'])
            b = int(row[1]['bundle_id'])
            B_bi[(b, i)] = bid
    return B_bi


def create_A_bp(df_bundle):
    """
    :param df_bundle:
    :return: return dict A_bp. If the part is not in bundle b there is no value in dict.
    """
    A_bp = {}
    for row in df_bundle.iterrows():
        for p in row[1]['part_ids']:
            A_bp[(row[0], p)] = 1
    return A_bp


class Parameters:
    def __init__(self, df_bidding, df_bundles):
        self.B_bi = create_B_bi(df_bidding)
        self.A_bp = create_A_bp(df_bundles)

        self.B = set(list(zip(*self.B_bi.keys()))[0])
        self.I = set(list(zip(*self.B_bi.keys()))[1])
        self.P = set(list(zip(*self.A_bp.keys()))[1])


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
            key = (i+min_index_row, j+min_index_col)
            matrix[i, j] = dictionary[key].solution_value()
    return matrix


def solve_bidding_problem(bids, bundles):
    parameters = Parameters(bids.df_bids, bundles.df_bundles)
    model = gp.Model("Winner_Determination_Problem")
    model.Params.LogToConsole = 0

    I = parameters.I
    B = parameters.B
    P = parameters.P

    list_bi = [(b, i) for i in I for b in B]
    W_bi = model.addVars(list_bi, vtype=GRB.BINARY, name="W_bi")

    # CONSTRAINTS
    model.addConstrs(gp.quicksum(W_bi[(b, i)] for i in I) <= 1 for b in B)

    model.addConstrs(gp.quicksum(W_bi[(b, i)] for b in B) <= 1 for i in I)

    for b in B: model.addSOS(GRB.SOS_TYPE1, [W_bi[(b, i)] for i in I])

    for i in I: model.addSOS(GRB.SOS_TYPE1, [W_bi[(b, i)] for b in B])

    model.addConstrs(gp.quicksum(parameters.A_bp.get((b, p), 0) * W_bi[(b, i)] for b in B for i in I) == 1 for p in P)

    model.setObjective(gp.quicksum(W_bi[(b, i)] * parameters.B_bi.get((b, i), 0) for i in I for b in B), GRB.MINIMIZE)

    model.setParam("TimeLimit", 120*1000)
    model.optimize()
    solver_succesful = False

    status = model.Status

    if status == GRB.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
    if status == GRB.OPTIMAL:
    #    print('The optimal objective is %g' % model.ObjVal)
        solver_succesful = True
    if status != GRB.INF_OR_UNBD and status != GRB.INFEASIBLE and status != GRB.OPTIMAL:
        print('Optimization was stopped with status %d' % status)

    W_bi_dict = create_binary_solution_dict(W_bi)
    return W_bi_dict

def solve_winner_determination_problem(bids, bundles, time_record=None):
    print("--------- Step 4 - winner determination ---------")
    if time_record: time_record.start_measurement("4-Winner-Determination")
    W_bi = solve_bidding_problem(bids, bundles)
    bids.set_flag_winning_bid(W_bi)
    if time_record: time_record.stop_measurement()


if __name__ == "__main__":
    parent_folder = "C:/Users/dozehetner/Seafile/03_Research/02_Decentralized_Planning/03_Programming/01_Input_Data/Case_Study_IJPE"

    file_names = os.listdir(parent_folder)
    files_abs_path = [parent_folder + "/" + file_name for file_name in file_names]
    df_parts, df_sites, df_materials, df_transport, df_parameters, parameters = read_files(files_abs_path[1])
    df_parts.loc[:, 'request_part'] = True
    df_parts = df_parts.head(20)
    df_parts.loc[:, 'machine'] = 0
    print("-----------bundle generation------------------------")
    df_bundles, dict_computational_time_step_2 = Bundle_Generation_2_LP_GUROBI.create_bundles(df_parts, df_transport, parameters)
    print("-----------bidding------------------------")
    df_bidding, dict_computational_time_step_3 = Bidding_3_fixed_batches_GUROBI.create_bidding_df(df_parts, df_bundles, df_sites, df_transport, parameters)

    df_bidding.to_csv("Bidding_Test.csv")
    df_bundles.to_csv("Bundles_Test.csv")
    print("-----------winner determination------------------------")

    df_bidding, dict_computational_time_step_4 = solve_winner_determination_problem(
                df_bidding, df_bundles)

