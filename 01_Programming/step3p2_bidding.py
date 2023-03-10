import numpy as np
import pandas as pd
import os
from Input.file_management import read_files
from Bidding.Bids import Bids
from Scheduling.LP.single_machine_scheduling import solve_instance


def return_transport_time_hours(origin, destination, df_transport):
    transport_time = float(df_transport[df_transport["destination"]==origin][destination])*24
    return transport_time

def create_matrix_in_hours(time_j):
    matrix = np.zeros(len(time_j)+1)
    for j in range(len(time_j)):
        matrix[j+1] = time_j[j+1].solution_value()/3600.0
    return matrix

def create_df_parts_with_bundles(parts, bundles, bundle_id, unique_machine_id):
    df_parts_for_machine = parts.get_df_parts_of_machine_wo_request(unique_machine_id)
    for part in bundles.get_parts_of_bundle(bundle_id):
        df_parts_for_machine = \
            pd.concat([df_parts_for_machine, parts.df_parts.loc[parts.df_parts["part_id"] == part]], ignore_index=True)
    return df_parts_for_machine

def solve_all_bundles_for_machine(parts, bundles, machine, input_dfs):
    """
    :param df_parts:
    :param unique_machine_id:
    :param machine:
    :param input_dfs:
    :return: bids of one machine in form of a df, each machine needs to deliver bids to all bundles,
            + costs of all parts without request parts (bundle index: -2)
            + , + costs of all initial parts (bundle index: -1)
    """
    df_parts_for_machine = parts.get_df_parts_of_machine_wo_request(machine.unique_machine_id)
    result = solve_instance(machine, df_parts_for_machine, input_dfs)
    result.set_bundle_id(-2)
    df_bidding = result.costs.to_frame().T

    for bundle_index in bundles.get_indices_of_bundles():
        df_parts_for_machine = create_df_parts_with_bundles(parts, bundles, bundle_index, machine.unique_machine_id)
        result = solve_instance(machine, df_parts_for_machine, input_dfs)
        result.set_bundle_id(bundle_index)
        df_bidding = pd.concat([df_bidding, result.costs.to_frame().T], ignore_index=True)
    return df_bidding


def solve_bundle_for_bid(estimated_bid, bundles, parts, input_dfs):
    bundle_id = estimated_bid['bundle_id']
    parts_in_bundle = bundles.get_parts_of_bundle(bundle_id)
    unique_machine_id = estimated_bid['unique_machine_id']
    if estimated_bid['request_true_bid']:
        df_parts_for_machine = pd.concat([parts.get_df_parts_of_part_list(parts_in_bundle),
                                          parts.get_df_parts_of_machine_wo_request(unique_machine_id)], ignore_index=True)
    else:
        df_parts_for_machine = pd.DataFrame()
    machine = input_dfs.get_machine_with_unique_machine_id(unique_machine_id)
    result = solve_instance(machine, df_parts_for_machine, input_dfs)
    if not estimated_bid['request_true_bid']: result.set_max_sr_cost()
    result.set_bundle_id(bundle_id)
    return result.costs.to_frame().T


def create_bidding_df(parts, bundles, input_dfs, time_record, bids_estimated=None):
    """
    :param parts: parts which are forwarded to the auctioneer
    :param bundles: the bundles created by the auctioneer
    :param input_dfs: all input dfs (parts, sites, parameters)
    :param bids_estimated: the bids estimated from the predictor
    :return: new bids, only the best estimated bids will be considered. This is marked by the flag "request_true_bid"
    """
    print("--------- Step 3 - bidding ---------")
    time_record.start_measurement("3-Bidding-Accurate")
    bids = Bids()

    if bids_estimated is None:
        for machine in input_dfs.df_machines.iterrows():
            time_record.start_agent_measurement()
            df_bidding_machine = solve_all_bundles_for_machine(parts, bundles, machine[1], input_dfs)
            bids.add_bids_to_overall_df_bid(df_bidding_machine)
            time_record.stop_agent_measurement()
    else:
        for estimated_bid in bids_estimated.df_bids.iterrows():
            df_cost_real_bid = solve_bundle_for_bid(estimated_bid[1], bundles, parts, input_dfs)
            bids.add_bids_to_overall_df_bid(df_cost_real_bid)

    time_record.stop_measurement()
    bids.compute_marginal_costs()
    return bids


if __name__ == "__main__":
    parent_folder_input = "C:/Users/dozehetner/Seafile/03_Research/02_Decentralized_Planning/06_Instances/01_Case_Study_IJPE_new_bundle_param_new_prices/01_Input_Data"
    
    file_names = os.listdir(parent_folder_input)
    files_abs_path = [parent_folder_input + "/" + file_name \
                      for file_name in file_names]
    
    df_parts, df_sites, df_materials, df_transport, df_parameters, parameters =\
        read_files(files_abs_path[52])
    
    df_parts.loc[:, 'request_part'] = True
    df_parts = df_parts
    df_parts.loc[:, 'machine']=0
    df_bundles, dict_computational_time_step_2 = \
        Bundle_Generation_2_LP_GUROBI.create_bundles(df_parts, df_transport, df_sites, parameters)
    
    df_bundles = df_bundles.tail(1)
    print("-----------start bidding------------------------")
    df_bidding, dict_computational_time_step_3 = \
        create_bidding_df(df_parts, df_bundles, df_sites, df_transport, parameters)

