
import pandas as pd
from step3p2_bidding import create_df_parts_with_bundles
from Bidding.Bids import Bids


def estimate_all_bundles_for_machine(parts, bundles, machine, input_dfs, predictor):
    """
    creates estimate bidding df for all bundles and one single machine
    :param df_parts: already scheduled parts
    :param df_bundles: created bundles of step 2
    :param machine: machine which needs to estimate bundle costs
    :param input_dfs: all input df required for
    :param predictor: predictor which is already trained
    :return:get_df_parts_of_machine_wo_request
    """
    df_parts_for_machine = parts.get_df_parts_of_machine_wo_request(machine.unique_machine_id)

    estimated_costs_bundle_wo_request_parts = predictor.predict_costs(df_parts_for_machine, machine, input_dfs)
    estimated_costs_bundle_wo_request_parts['bundle_id'] = -2
    df_bidding = pd.Series(estimated_costs_bundle_wo_request_parts).to_frame().T

    for bundle_index in range(len(bundles.df_bundles)):
        df_parts_for_machine = create_df_parts_with_bundles(parts, bundles, bundle_index, machine.unique_machine_id)
        costs_bundle = predictor.predict_costs(df_parts_for_machine, machine, input_dfs)
        costs_bundle['bundle_id'] = bundle_index
        df_bidding = pd.concat([df_bidding, pd.Series(costs_bundle).to_frame().T], ignore_index=True)
    return df_bidding


def create_bidding_estimate(parts, bundles, input_dfs, predictor, time_record):
    """
    creates estimate bidding df for all bundles and all machines
    :param df_parts:
    :param df_bundles:
    :param input_dfs:
    :param predictor:
    :return: DataFrame with estimated bids, and computational time
    """
    print("---------- Step 3.1 - estimation ---------")
    time_record.start_measurement('3-Bidding_estimate')
    bids = Bids(estimate=True)
    for machine in input_dfs.df_machines.iterrows():
        time_record.start_agent_measurement()
        df_bidding_machine = estimate_all_bundles_for_machine(parts, bundles, machine[1], input_dfs, predictor)
        bids.add_bids_to_overall_df_bid(df_bidding_machine)
        time_record.stop_agent_measurement()
    bids.compute_marginal_costs()
    bids.set_flag_promising_machines_for_bundle(4)
    return bids






