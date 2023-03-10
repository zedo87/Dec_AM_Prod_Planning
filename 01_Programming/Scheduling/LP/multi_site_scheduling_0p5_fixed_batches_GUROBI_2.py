import gurobipy as gp
from gurobipy import GRB
import os
from model import ModelMultiSite
from Scheduling.result_sched import ResultSchedMultiSite
from Scheduling.parameters import ParametersMultiSite
from Input.file_management import InputDataFrames


def solve_schedule(params):
    """
    THIS MODEL ONLY WORKS IF SITE PARAMETERS ARE THE SAME FOR ALL SITES!!! JUST FOR TESTING!
    :param params:
    :return:
    """
    grb_model = gp.Model("single_site_scheduling")
    grb_model.Params.LogToConsole = 1

    model = ModelMultiSite(params, grb_model)

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

    #grb_model.setParam("TimeLimit", 300)
    #grb_model.setParam("MIPFocus", 2)
    grb_model.setParam('MIPGap', 0.05)
    #model.setParam("IntFeasTol", 0.005)
    #grb_model.write("test.LP")
    grb_model.optimize()

    status = grb_model.Status
        
    if status == GRB.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
    if status != GRB.INF_OR_UNBD and status != GRB.INFEASIBLE and status != GRB.OPTIMAL:
        print('Optimization was stopped with status %d' % status)

    result = ResultSchedMultiSite(model)
    return result

    
if __name__ == "__main__":
    parent_folder = "C:/Users/dozehetner/Seafile/03_Research/09_DecPlanning_ML_Support/04_Experiments/01_Case_Study/01_Input_Data"
    file_names = os.listdir(parent_folder)
    files_abs_path = [parent_folder + "/" + file_name for file_name in file_names]
    index = 50
    file_name = files_abs_path[index]
    case_name = file_names[index][:5]
    print("Solve case name: %s" % case_name)
    input_dfs = InputDataFrames(file_name)
    params = ParametersMultiSite(input_dfs)
    result = solve_schedule(params)
    print(result.costs)
    pass


