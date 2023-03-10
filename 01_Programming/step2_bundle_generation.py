import gurobipy as gp
from gurobipy import GRB
import numpy as np
import os
import pandas as pd
from Input.file_management import read_files
from Post_Processing.gurobi_post_process import create_binary_solution_dict
from Bundling.Bundle import Bundles

def create_bundle_fitness_matrix(df_parts, df_bundles, input_dfs):
    last_level = df_bundles['level'].max()
    df_bundle_last_level = df_bundles[df_bundles['level'] == last_level]
    B = df_bundle_last_level.index.to_list()
    F_bb = {}
    for b in B:
        for b_tick in B:
            part_list_bundle_1 = df_bundle_last_level.loc[b]['part_ids']
            part_list_bundle_2 = df_bundle_last_level.loc[b_tick]['part_ids']
            df_parts_new_bundle = return_part_list_of_new_bundle(df_parts, part_list_bundle_1, part_list_bundle_2)
            if b != b_tick:
                F_bb[(b, b_tick)] = compute_fitness_of_bundle(df_parts_new_bundle, input_dfs, 3, 1, 1000, 0.1)
            else: F_bb[(b ,b_tick)] = 0
    return F_bb


def return_part_list_of_new_bundle(df_parts, list_bundle_1, list_bundle_2):
    list_parts_new_bundle = []
    list_parts_new_bundle.extend(list_bundle_1)
    list_parts_new_bundle.extend(list_bundle_2)
    df_parts_new_bundle = df_parts[df_parts['part_id'].isin(list_parts_new_bundle)].copy()
    return df_parts_new_bundle


def compute_fitness_of_bundle(df_parts, input_dfs, alpha, beta, gamma, delta):
    fitness = 0
    fitness += compute_fitness_due_to_height(df_parts, alpha)
    fitness += compute_fitness_due_to_transport(df_parts, input_dfs, beta)
    fitness += compute_fitness_due_to_materials(df_parts, gamma)
    fitness += compute_fitness_due_to_inventory(df_parts, input_dfs.sr_parameters, delta)
    return fitness


def compute_fitness_due_to_inventory(df_parts, sr_parameters, delta):
    df_parts_new = pd.DataFrame.copy(df_parts)
    df_parts_new.loc[:, 'timespan'] = df_parts_new['due_date'] - sr_parameters.start_date
    df_parts_new.loc[:, 'timespan_hours'] = df_parts_new['timespan'].dt.days * 24 \
                                          + df_parts_new['timespan'].dt.seconds / 3600.0
    hours_std = df_parts_new['timespan_hours'].std()
    fitness = delta*hours_std
    return fitness


def compute_fitness_due_to_materials(df_parts, gamma):
    number_of_materials = len(df_parts['material_id'].unique().tolist())
    fitness = number_of_materials * gamma
    return fitness


def compute_fitness_due_to_transport(df_parts, input_dfs, beta):
    number_of_parts = len(df_parts)
    fitness = 0
    for p in range(number_of_parts):
        for p_tick in range(number_of_parts):
            if p != p_tick:
                delivery_time = return_delivery_time(input_dfs,
                                                     df_parts.iloc[p]['destination'],
                                                     df_parts.iloc[p_tick]['destination'])
                fitness += delivery_time / number_of_parts * beta
    return fitness

def return_delivery_time(input_dfs, origin, destination):
    delivery_time = float(input_dfs.df_transport[input_dfs.df_transport['destination'] == origin][destination]) * 24.0
    return delivery_time

def compute_fitness_due_to_height(df_parts, alpha):
    height_std = df_parts['height'].std()
    fitness = alpha*height_std
    return fitness


class Parameters:
    def __init__(self, df_parts, df_bundles, input_dfs):
        self.F_bb = create_bundle_fitness_matrix(df_parts, df_bundles, input_dfs)
        self.B = set(list(zip(*self.F_bb.keys()))[0])
        self.number_of_bundles = len(self.B)
        self.number_of_merges = np.floor(self.number_of_bundles/2.0)
        self.number_of_single_bundles = self.number_of_bundles - self.number_of_merges*2

def solve(parameters):
    model = gp.Model('Bundle_Generation')
    model.Params.LogToConsole = 0
    model.setParam("TimeLimit", 300) #
    
    B = parameters.B
    list_bb_tick = [(b, b_tick) for b in B for b_tick in B]
    M_bb = model.addVars(list_bb_tick, vtype=GRB.BINARY, name="M_bb")

     # CONSTRAINTS
    #model.addConstrs(gp.quicksum(M_bb[(b,b_tick)] for b_tick in B) <= 1 for b in B)
    for b in B:
            model.addSOS(GRB.SOS_TYPE1, [M_bb[(b, b_tick)] for b_tick in B])
    
    model.addConstrs(gp.quicksum(M_bb[(b, b_tick)] for b_tick in B) +
                     gp.quicksum(M_bb[(b_tick, b)] for b_tick in B) <= 1 for b in B)
    
    model.addConstrs(gp.quicksum(M_bb[(b, b_tick)] for b in B) <= 1 for b_tick in B)
        
    model.addConstrs(gp.quicksum(M_bb[(b, b_tick)] for b in B) <= 1 for b in B for b_tick in B)
    model.addConstr(gp.quicksum(M_bb[(b, b_tick)] for b in B for b_tick in B if b > b_tick) == 0)
        
    model.addConstr(gp.quicksum(M_bb[(b, b_tick)] for b in B for b_tick in B) == parameters.number_of_merges)
    # OBJECTIVE FUNCTION
    model.setObjective(gp.quicksum(M_bb[(b, b_tick)]*parameters.F_bb[(b, b_tick)] for b in B for b_tick in B),
                       GRB.MINIMIZE)
    model.optimize()

    status = model.Status
    solver_succesful = False
        
    if status == GRB.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
    if status == GRB.OPTIMAL:
    #    print('The optimal objective is %g' % model.ObjVal)
        solver_succesful = True
    if status == 9:
        solver_succesful = True
    if status != GRB.INF_OR_UNBD and status != GRB.INFEASIBLE and status != GRB.OPTIMAL:
        print('Optimization was stopped with status %d' % status)

    return create_binary_solution_dict(M_bb)


def find_bundle_which_was_not_merged(M_bb):
    B = set(list(zip(*M_bb.keys()))[0])
    for b in B:
        merged = 0
        for b_prime in B:
            merged += M_bb[(b,b_prime)]
            merged += M_bb[(b_prime, b)]
        if merged == 0:
            break
    return b

def create_bundles_of_next_level(M_bb, df_bundles):
    B = set(list(zip(*M_bb.keys()))[0])
    df_new_level_of_bundles = pd.DataFrame()
    next_level = df_bundles['level'].max() + 1
    for b in B:
        for b_tick in B:
            if M_bb[(b, b_tick)] == 1:
                part_list = df_bundles.loc[b]['part_ids'].copy()
                part_list.extend(df_bundles.loc[b_tick]['part_ids'].copy())
                dict_bundle = {'part_ids': part_list,
                               'level': next_level}
                df_new_level_of_bundles = pd.concat([df_new_level_of_bundles,
                                                     pd.Series(dict_bundle).to_frame().T], ignore_index=True)
    return df_new_level_of_bundles



def return_single_bundle(M_bb, df_bundles):
    df_single_bundle = pd.DataFrame()
    bundle_index = find_bundle_which_was_not_merged(M_bb)
    next_level = df_bundles['level'].max()+1
    dict_bundle = {'part_ids': df_bundles.loc[bundle_index]['part_ids'], 'level': next_level}
    df_single_bundle = pd.concat([df_single_bundle, pd.Series(dict_bundle).to_frame().T], ignore_index=True)
    return df_single_bundle

def create_bundles(parts, input_dfs, time_record):
    print("---------- Step 2 - bundle generation ---------")
    time_record.start_measurement("2-Bundling")
    df_parts_for_bundles = parts.get_df_of_requested_parts()
    bundles = Bundles()
    bundles.create_initial_bundle(df_parts_for_bundles)
    last_level = 0
    if input_dfs.df_sites['number_of_machines'].sum() > 3:
        maximum_number_of_merge_levels = 3
    else:
        maximum_number_of_merge_levels = 4
    merge_necessary = True
    while merge_necessary:
        df_bundles_of_this_level = bundles.get_bundles_of_level(last_level)
        parameters = Parameters(df_parts_for_bundles, df_bundles_of_this_level, input_dfs)
        M_bb = solve(parameters)
        next_level_bundles = create_bundles_of_next_level(M_bb, df_bundles_of_this_level)
        if parameters.number_of_single_bundles == 1.0:  # if uneven bundles/parts to merge
            next_level_bundles = pd.concat([next_level_bundles,
                                           return_single_bundle(M_bb, df_bundles_of_this_level)], ignore_index=True)

        bundles.add_bundle_to_overall_df(next_level_bundles)
        last_level = bundles.get_highest_level_of_bundles()
        if (last_level >= maximum_number_of_merge_levels) \
                or (len(df_parts_for_bundles) == len(bundles.df_bundles['part_ids'].iloc[-1])):
            merge_necessary = False

    bundles.reindex_bundles()
    time_record.stop_measurement()
    return bundles



if __name__ == "__main__":
    parent_folder = "C:/Users/dozehetner/Seafile/03_Research/02_Decentralized_Planning/03_Programming/01_Input_Data/Case_Study_IJPE"
    
    file_names = os.listdir(parent_folder)
    files_abs_path = [parent_folder + "/" + file_name for file_name in file_names]
    
    df_parts, df_sites, df_materials, df_transport, df_parameters, parameters = read_files(files_abs_path[1])
    df_parts.loc[:,'request_part'] = True
    #df_parts = df_parts.head(17)
    df_bundles, dict_computational_time_step_2 = create_bundles(df_parts, df_transport, parameters)
