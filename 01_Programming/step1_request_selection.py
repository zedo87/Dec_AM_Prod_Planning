from Other.Random_Sequence_Generator import create_structured_random_sequences
import pandas as pd

def return_transport_time_hours(df_transport, origin, destination):
    transport_time = float(df_transport[df_transport['destination']==origin][destination])*24
    return transport_time

def determine_transport_costs(df_parts, input_dfs):
    chi = 0
    for p in range(len(df_parts)):
        transport_time = return_transport_time_hours(input_dfs.df_transport, df_parts.iloc[p]["origin"],
                                                     df_parts.iloc[p]["destination"])
        chi += df_parts.iloc[p]["price"] * input_dfs.sr_parameters["psi"] \
             + input_dfs.sr_parameters['omega'] * transport_time
    return chi

def determine_production_costs(df_parts, input_dfs, machine):
    costs_due_height = 0.0
    costs_due_volume = 0.0
    batches = df_parts['batch_id'].unique().tolist()
    for batch in batches:
        df_part_batch = df_parts[df_parts['batch_id'] == batch]
        if len(df_part_batch) > 0:
            max_height = df_part_batch['height'].max()
            volume = (df_part_batch['height'] * df_part_batch['length'] * df_part_batch['width']).sum()
            costs_due_height += max_height * input_dfs.sr_parameters['max_speed_z'] / input_dfs.sr_parameters[
                'resolution'] * machine['production_cost_factor'] / 3600
            costs_due_volume += volume * input_dfs.sr_parameters["max_speed_xy"] / input_dfs.sr_parameters['resolution'] * \
                                machine['production_cost_factor'] / 3600
    return costs_due_height, costs_due_volume

def determine_setup_costs(df_parts, machine):
    setup_costs = 0
    if len(df_parts) > 0:
        number_of_materials = len(df_parts['material_id'].unique().tolist())
        number_of_batches = len(df_parts['batch_id'].unique().tolist())
        setup_costs += machine['setup_cost_factor'] * \
                       machine['setup_time_batching'] * \
                       number_of_batches
        setup_costs += machine['setup_cost_factor'] * \
                       machine['setup_time_material'] * \
                       number_of_materials
    return setup_costs

def estimate_costs(df_parts,  input_dfs, machine):
    costs = 0
    costs += determine_setup_costs(df_parts, machine)
    costs += sum(determine_production_costs(df_parts, input_dfs, machine))
    costs += determine_transport_costs(df_parts, input_dfs)
    return costs


def compute_shapley_value_of_parts_approximation(parts, input_dfs, time_record):
    unique_machines_ids = parts.get_all_unique_machine_ids()
    for unique_machine_id in unique_machines_ids:
        time_record.start_agent_measurement()
        machine = input_dfs.df_machines[input_dfs.df_machines['unique_machine_id'] == unique_machine_id].iloc[0]
        set_and_compute_Shapley_cost_of_machine(parts, input_dfs, machine)
        time_record.stop_agent_measurement()


def compute_marginal_costs_of_sequence(df_parts, input_dfs, machine, sequence):
    costs_previous_subset_parts = 0
    df_marginal_costs = pd.DataFrame()
    for sequence_index in range(len(sequence)):
        part_list = sequence[0:sequence_index+1]
        df_parts_subset = df_parts[df_parts['part_id'].isin(part_list)]
        costs_subset_parts = estimate_costs(df_parts_subset, input_dfs, machine)
        costs_order = costs_subset_parts - costs_previous_subset_parts
        costs_previous_subset_parts = costs_subset_parts
        marginal_costs_sr = pd.Series({
            'part_id': sequence[sequence_index],
            'marginal_costs': costs_order,
            'unique_machine_id': machine.unique_machine_id})
        df_marginal_costs = pd.concat([df_marginal_costs, marginal_costs_sr.to_frame().T], ignore_index=True)
    return df_marginal_costs


def set_and_compute_Shapley_cost_of_machine(parts, input_dfs, machine):
    list_parts = parts.get_part_list_of_unique_machine_id(machine.unique_machine_id)
    sequences_approx = create_structured_random_sequences(list_parts, 1)
    df_marginal_costs = pd.DataFrame()
    for sequence in sequences_approx:
        df_marginal_costs = pd.concat([df_marginal_costs,
                                compute_marginal_costs_of_sequence(parts.df_parts, input_dfs, machine, \
                                                       sequence)], ignore_index=True)
    parts.set_Shapley_costs_to_parts(df_marginal_costs)


def flag_parts(df_parts, margin_limit):
    df_parts['request_part'] = df_parts['margin'] < margin_limit
    return df_parts

def select_request_parts(parts, input_dfs, time_record):
    print("--------- Step 1 - Request Selection ---------")
    time_record.start_measurement("1-Request")
    compute_shapley_value_of_parts_approximation(parts, input_dfs, time_record)
    parts.set_margin_to_parts()
    parts.set_flag_parts_for_request(input_dfs.sr_parameters['target_margin'])
    time_record.stop_measurement()
