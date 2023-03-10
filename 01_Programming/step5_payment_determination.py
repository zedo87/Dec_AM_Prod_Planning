import pandas as pd
from math import factorial
import random
from random import sample
from step4_winner_determination import solve_winner_determination_problem
from Other.Random_Sequence_Generator import create_structured_random_sequences
from Bidding.Bids import Bids


def compute_shapley_value_of_parts_approximation(df_parts, input_dfs):
    new_df_parts = pd.DataFrame()
    df_part_for_machine = compute_shapley_indicators_of_parts_new_approach(df_parts, input_dfs)
    new_df_parts = pd.concat([new_df_parts, df_part_for_machine], ignore_index=True)
    return new_df_parts


def create_random_permutations_of_part_list(df_parts, number_of_samples, seed):
    permutation_list = []
    part_list = df_parts['part_id'].to_list()
    number_of_parts = len(part_list)
    seed_intern = seed
    max_number_of_permutation = factorial(number_of_parts)
    while(len(permutation_list)<min(max_number_of_permutation,number_of_samples)):
        random.seed(seed_intern)
        new_permutation = sample(part_list, len(part_list))
        if new_permutation not in permutation_list:
            permutation_list.append(new_permutation)
        seed_intern += 1
    return permutation_list


def compute_shapley_indicator_of_sequence(df_parts, sequence, input_dfs):
    costs_previous_subset_parts = 0
    df_marginal_costs = pd.DataFrame()
    for sequence_index in range(len(sequence)):
        part_list = sequence[0:sequence_index+1]
        df_parts_subset = df_parts[df_parts['part_id'].isin(part_list)]
        costs_subset_parts = compute_shapley_value_indicator(df_parts_subset, input_dfs)
        costs_order = costs_subset_parts - costs_previous_subset_parts
        costs_previous_subset_parts = costs_subset_parts
        marginal_costs_dict={
            'part_id': sequence[sequence_index],
            'marginal_costs':costs_order}
        df_marginal_costs = pd.concat([df_marginal_costs, pd.Series(marginal_costs_dict).to_frame().T],
                                      ignore_index=True)
    return df_marginal_costs


def compute_shapley_indicators_of_parts_new_approach(df_parts, input_dfs):
    """
    Computes the Shapley indicated for parts with an approximation approach.
    A structured random sequence is used for this
    :param df_parts:
    :param input_dfs:
    :return:
    """
    sequences_approx = create_structured_random_sequences(list(df_parts['part_id']), 1)
    df_marginal_costs = pd.DataFrame()
    for sequence in sequences_approx:
         df_marginal_costs = pd.concat([df_marginal_costs,
                                        compute_shapley_indicator_of_sequence(df_parts, sequence, input_dfs)],
                                       ignore_index=True)
    df_marginal_costs = df_marginal_costs\
                        .groupby('part_id')\
                        .mean()\
                        .reset_index()\
                        .rename(columns={'marginal_costs': 'shapley_ind'})
    df_parts = df_parts.merge(df_marginal_costs, how='left', on='part_id')
    return df_parts


def compute_Z_zero(bids, bundles):
    unique_machine_ids = bids.df_bids['unique_machine_id'].unique()
    Z_0_i = {}

    for i in unique_machine_ids:
        bids_wo_machine = Bids(estimate=False, df_bids = bids.df_bids[bids.df_bids['unique_machine_id'] != i].copy())
        bids_wo_machine.reset_flags_winning_bid()
        solve_winner_determination_problem(bids_wo_machine, bundles)
        Z_0_i[i] = bids_wo_machine.get_revenue_of_auction()
    return Z_0_i


def compute_b_i(bids):
    machines = bids.get_unique_machine_ids()
    b_i = {}
    for i in machines:
        b_i[i] = bids.get_winning_bid_value_of_machine(i)
    return b_i


def compute_p_i(b_i, Z_star, Z_0_i):
    unique_machine_ids = b_i.keys()
    p_i = {}
    for i in unique_machine_ids:
        p_i[i] = b_i[i] - Z_star + Z_0_i[i]
    return p_i

def determine_payments(bids, bundles):
    Z_star = bids.get_revenue_of_auction()
    Z_0_i = compute_Z_zero(bids, bundles)
    b_i = compute_b_i(bids)
    p_i = compute_p_i(b_i, Z_star, Z_0_i)
    bids.set_payment(p_i)


def compute_transport_costs_of_bundle(origin, df_parts, input_dfs):
    df_parts_with_transport_costs = df_parts.copy()
    number_of_parts = len(df_parts)
    df_parts_with_transport_costs.loc[:, 'transport_costs'] = 0
    column_index_trans_costs = df_parts_with_transport_costs.columns.to_list().index('transport_costs')
    for p in range(number_of_parts):
        destination = df_parts_with_transport_costs.iloc[p]['destination']
        price_of_part = df_parts_with_transport_costs.iloc[p]['price']
        duration = input_dfs.df_transport[input_dfs.df_transport['destination'] == origin][destination]*24
        transport_costs = price_of_part*input_dfs.sr_parameters['psi'] + duration*input_dfs.sr_parameters['omega']
        df_parts_with_transport_costs.iat[p, column_index_trans_costs] = transport_costs
    return df_parts_with_transport_costs


def compute_shapley_value_indicator(df_parts, input_dfs):
    if len(df_parts) == 0:
        shapley_indicator = 0
    else:
        tau = input_dfs.df_sites.iloc[0]['production_cost_factor']
        sigma = input_dfs.df_sites.iloc[0]['setup_cost_factor']
        duration_setup_material = input_dfs.df_sites.iloc[0]['setup_time_material']
        setup_time_batching = input_dfs.df_sites.iloc[0]['setup_time_batching']
        number_of_materials = len(df_parts['material_id'].unique())
        shapley_indicator = number_of_materials*sigma*(duration_setup_material+setup_time_batching)
        for part in df_parts.iterrows():
            shapley_indicator += part[1]['height']*input_dfs.sr_parameters['max_speed_z'] / 3600.0 * tau
            shapley_indicator += part[1]['area']*part[1]['height']*input_dfs.sr_parameters['max_speed_xy'] / 3600.0 * tau
    return shapley_indicator


def compute_payments_for_each_part(payment_bundle_vcg, df_parts, input_dfs):
    """
    Uses payments for one bundle 'payment_bundle_vcg and determines the costs for each part of the bundle.
    The result of the computation is aded to df_parts on column 'payment_vcg
    :param payment_bundle_vcg:
    :param df_parts:
    :param input_dfs:
    :return:
    """
    df_parts_with_payment = df_parts.copy()
    v_N = compute_shapley_value_indicator(df_parts_with_payment, input_dfs)
    df_parts_with_payment = compute_shapley_value_of_parts_approximation(df_parts_with_payment, input_dfs)
    df_parts_with_payment.loc[:, 'payment_vcg_wo_TRANS'] = 0.0
    P = df_parts_with_payment.index.to_list()
    for p in P:
        shapley_indicator_of_part = df_parts_with_payment.loc[p]['shapley_ind']
        payment_of_part_vcg = payment_bundle_vcg * shapley_indicator_of_part / v_N
        df_parts_with_payment.at[p, 'payment_vcg_wo_TRANS'] = payment_of_part_vcg
    return df_parts_with_payment


def determine_payments_and_shared_costs(bids, bundles, parts, input_dfs, time_record):
    """
    determines the payments for each part and adds it to df parts
    :param bids:
    :param bundles:
    :param df_parts:
    :param input_dfs:
    :return:
    """
    print("--------- Step 5 - payment determination ---------")
    time_record.start_measurement("5-Payment Determination")
    df_parts_new = parts.get_df_parts()

    bundles.set_winning_bid_to_df_bundles(bids)
    determine_payments(bids, bundles)

    df_parts_new.loc[:, 'payment_vcg'] = 0.0
    df_parts_new.loc[:, 'transport_costs'] = 0.0
    df_parts_new.loc[:, 'unique_machine_id_new'] = None
    df_parts_new.loc[:, 'new_origin'] = None
    df_parts_new.loc[:, 'bundle'] = None
    for bid in bids.df_bids.iterrows():
        if bid[1]['winning_bid'] is True:
            costs_to_share_vcg = bid[1]['payment']
            bundle_id = int(bid[1]['bundle_id'])
            location = bid[1]['location']
            part_list = bundles.get_parts_of_bundle(bundle_id)
            if len(part_list) > 0:
                df_part_bundle = parts.get_df_parts_of_part_list(part_list)
                df_parts_bundle_with_transport_costs = compute_transport_costs_of_bundle(location, df_part_bundle, input_dfs)\
                                                       .copy()
                df_parts_bundle_with_transport_costs.loc[:, 'unique_machine_id_new'] = bid[1]['unique_machine_id']
                df_parts_bundle_with_transport_costs.loc[:, 'new_origin'] = bid[1]['location']
                df_parts_bundle_with_transport_costs.loc[:, 'bundle_id'] = bid[1]['bundle_id']

                costs_to_share_vcg -= df_parts_bundle_with_transport_costs['transport_costs'].sum()
                df_parts_with_payments = compute_payments_for_each_part(costs_to_share_vcg,
                                                                        df_parts_bundle_with_transport_costs,
                                                                        input_dfs)
                parts.set_payments(df_parts_with_payments)
    time_record.stop_measurement()
