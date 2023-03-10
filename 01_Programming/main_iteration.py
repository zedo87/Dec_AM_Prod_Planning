import os
import copy

from Scheduling.LP.single_site_scheduling_0p5_fixed_batches_GUROBI_2 import solve_single_site_problem_for_each_site
from step1_request_selection import select_request_parts
from step2_bundle_generation import create_bundles
from step3p2_bidding import create_bidding_df
from step3p2_bidding import solve_instance
from step3p1_bidding_estimate import create_bidding_estimate
from Bidding.predictor import Predictor
from step4_winner_determination import solve_winner_determination_problem
from step5_payment_determination import determine_payments_and_shared_costs
from Post_Processing.result_framework import Results
from Input.file_management import *
from step6_drawback import individual_rationality
from Other.time_record import TimeRecord

#predictor = Predictor()


def solve_case(filename, case_name, case_id, activate_estimation):
    time_record = TimeRecord()
    input_dfs = InputDataFrames(filename)
    df_result_case_all_its = pd.DataFrame()
    problem_successfully_solved, parts, df_costs = solve_single_site_problem_for_each_site(input_dfs, time_record)

    iteration_index = 0
    iteration_necessary = True
    result = Results(case_id, case_name)

    for machine in input_dfs.df_machines.iterrows():
        print("Solve Single Machine Problem for machine %s " % machine[1]['unique_machine_id'])
        df_parts_for_machine = parts.get_df_parts_of_machine(machine[1].unique_machine_id)
        result_sched = solve_instance(machine[1], df_parts_for_machine, input_dfs)
        result.add_initial_result_of_machine(result_sched)

    print(result.get_sum_of_initial_cost())

    print("Problem solve: %s " % problem_successfully_solved)
    if problem_successfully_solved:
        select_request_parts(parts, input_dfs, time_record)

        if not parts.get_are_parts_with_requests_available():
            print("No parts for request available - abort case")
            iteration_necessary = False
        
        while iteration_necessary:

            bundles = create_bundles(parts, input_dfs, time_record)

            estimated_bids = create_bidding_estimate(parts, bundles, input_dfs, predictor, time_record)
            if not activate_estimation: estimated_bids = None
            bids = create_bidding_df(parts, bundles, input_dfs, time_record, estimated_bids)
            solve_winner_determination_problem(bids, bundles, time_record)
            determine_payments_and_shared_costs(bids, bundles, parts, input_dfs, time_record)
            result.add_reassigned_results(parts, bids)
            another_iteration_necessary = individual_rationality(parts, result, iteration_index)
            iteration_index += 1
            iteration_necessary = another_iteration_necessary
            if iteration_necessary: time_record.add_new_iteration()
            print(result.get_sum_of_costs_of_last_iteration())

    result_df = result.get_result_df()
    result_df.loc[:, 'estimate'] = activate_estimation
    df_result_case_all_its = pd.concat([df_result_case_all_its, result_df], ignore_index=True)
    time_record.set_case_name_and_id_to_df(case_name, case_id)
    time_record.df_overall_computational_times.loc[:, 'estimate'] = activate_estimation
    df_computational_time = time_record.get_df_computation_time()
    return problem_successfully_solved, df_result_case_all_its, df_computational_time


if __name__ == "__main__":

    folder_instances = "C:/Users/dozehetner/Seafile/03_Research/09_DecPlanning_ML_Support/04_Experiments/"
    case_name = "02_Case_Study_Submission"
    folder_case = folder_instances + case_name
    parent_folder_input = folder_case +  "/01_Input_Data"
    activate_estimation = False
    folder_output = folder_case + "/02_Output_Data"
    output_folder_path = folder_output
    filename_output_result = "overall_result.xlsx"
    output_file_path_result = output_folder_path + "/" + filename_output_result
    filename_output_computational_time = "computational_time.xlsx"
    path_output_computational_time = output_folder_path + "/" + filename_output_computational_time

    file_names = os.listdir(parent_folder_input)

    overall_result_df, df_computational_time = \
        get_old_results(output_file_path_result, path_output_computational_time)

    scenarios_in_input = set([x[:-5] for x in file_names])
    scenarios_computed = set(overall_result_df['case_name'].unique().tolist())

    scenarios_to_compute = scenarios_in_input.difference(scenarios_computed)

    file_names = sorted([scenario+".xlsx" for scenario in scenarios_to_compute])

    files_abs_path = [parent_folder_input + "/" + file_name for file_name in file_names]

    comment ='test_cases_for_submission'

    for file_index in range(len(files_abs_path)):
        case_id = file_names[file_index][:-5]
        print("Solving case: %s" % case_id)
        problem_successfully_solved, df_results_case, df_computational_time_case = \
            solve_case(files_abs_path[file_index], case_id, file_index, activate_estimation)
                
        df_results_case.loc[:, 'comment'] = comment
        overall_result_df = pd.concat([overall_result_df, df_results_case.copy()], ignore_index=True)
        overall_result_df.to_excel(output_file_path_result)

        df_computational_time_case.loc[:, 'comment'] = comment
        df_computational_time = pd.concat([df_computational_time, df_computational_time_case.copy()], ignore_index=True)
        df_computational_time.to_excel(path_output_computational_time)
            
