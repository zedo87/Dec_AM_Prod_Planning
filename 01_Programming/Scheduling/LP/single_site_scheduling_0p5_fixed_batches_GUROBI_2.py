import gurobipy as gp
import pandas as pd
from gurobipy import GRB
import os

from Input.file_management import read_files
from Input.parts import Parts
from Scheduling.parameters import ParametersSite
from Scheduling.LP.model import ModelSite
from Scheduling.result_sched import ResultSchedSite


def solve_schedule(params):
    grb_model = gp.Model("single_site_scheduling")
    grb_model.Params.LogToConsole = 0

    model = ModelSite(params, grb_model)

    model.build_part_in_print_bed_x()
    model.build_part_in_print_bed_y()
    model.build_collision_detection()
    model.build_all_parts_allocated()
    model.build_only_part_if_batch_active()

    model.build_all_part_allocated_speed_up()
    model.build_batch_height()
    model.build_batch_duration()
    model.build_end_time_part()
    model.build_end_time_part_speed_up()
    model.build_due_date_batch()
    model.build_start_time_before_due_date()

    model.build_batch_can_only_be_allocated_once_SOS()
    model.build_batch_can_not_be_own_successor()
    model.build_batch_can_only_be_successor_if_there_is_predecessor()
    model.build_last_batch_is_zero()
    model.build_avoid_circle_sequence()
    model.build_start_time_zero_if_batch_not_active()
    model.build_start_time_batch_after_predecessor()
    model.build_part_to_batch_with_same_material()
    model.build_part_to_batch_with_same_material_speed_up()

    model.build_objective_function()

    grb_model.setParam("TimeLimit", 1800)
    #grb_model.setParam("MIPFocus", 2)
    grb_model.setParam('MIPGap', 0.04)
    #model.setParam("IntFeasTol", 0.005)
    #grb_model.write("test.LP")
    grb_model.optimize()

    status = grb_model.Status
        
    if status == GRB.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
    if status != GRB.INF_OR_UNBD and status != GRB.INFEASIBLE and status != GRB.OPTIMAL:
        print('Optimization was stopped with status %d' % status)

    result = ResultSchedSite(model)
    return result

def solve_single_site_problem_for_each_site(input_dfs, time_record):
    print("--------- Step 0.5 - site scheduling ---------")
    time_record.start_measurement('0p5-Request')
    df_costs = pd.DataFrame()
    df_parts_overall_new = pd.DataFrame()
    k = 0
    problem_successfully_solved = True
    for site in input_dfs.df_sites.iterrows():
        time_record.start_agent_measurement()
        print("Solve single site problem of site %s" % site[1]['location'])
        df_parts_site = input_dfs.df_parts[input_dfs.df_parts['origin'] == site[1]['location']].copy()
        df_parts_site.loc[:, 'site_id'] = site[1]['site_id']
        if len(df_parts_site) > 0:
            parameters = ParametersSite(df_parts_site, input_dfs, site[1])
            result = solve_schedule(parameters)

            if result.solver_successful:
                df_parts_result = result.get_solution_to_parts_df()
                df_parts_new = pd.merge(df_parts_site, df_parts_result, on='part_id')
                df_parts_overall_new = pd.concat([df_parts_overall_new, df_parts_new], ignore_index=True)
                k += 1
        else:
            result = ResultSchedSite()
            result.set_solver_status(True)
        time_record.stop_agent_measurement()

        result.set_site_id(k)
        result.set_location(site[1]['location'])
        df_costs = pd.concat([df_costs, pd.Series(result.costs).to_frame().T], ignore_index=True)
        if not result.solver_successful: break


    time_record.stop_measurement()
    parts = Parts(df_parts_overall_new)
    parts.set_unique_machine_id(input_dfs)
    return problem_successfully_solved, parts, df_costs

    
if __name__ == "__main__":
    parent_folder = "C:/Users/dozehetner/Seafile/03_Research/02_Decentralized_Planning/03_Programming/01_Input_Data/Case_Study_IJPE_2"
    
    file_names = os.listdir(parent_folder)
    files_abs_path = [parent_folder + "/" + file_name for file_name in file_names]
    
    df_parts, df_sites, df_materials, df_transport, df_parameters, parameters = read_files(files_abs_path[3])
    #df_parts = df_parts.head(17)
    problem_successfully_solved, df_parts_scheduled, df_costs, dict_computational_time_step_p5 = \
        solve_single_site_problem_for_each_site(df_parts, df_transport, df_sites, df_parameters.iloc[0])


