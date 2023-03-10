import gurobipy as gp
from gurobipy import GRB
from Scheduling.parameters import ParametersMachine
from Scheduling.result_sched import ResultSchedMachine
from Scheduling.LP.model import ModelMachine

def solve_LP(params):
    grb_model = gp.Model("single_machine_schedule")
    grb_model.Params.LogToConsole = 1
    model = ModelMachine(params, grb_model)

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
    grb_model.setParam("TimeLimit", 180)
    #model.setParam("IntFeasTol", 0.01)
    #model.setParam("FeasibilityTol", 0.01)

    grb_model.optimize()
    status = grb_model.Status

    if status == GRB.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
    if status != GRB.INF_OR_UNBD and status != GRB.INFEASIBLE and status != GRB.OPTIMAL:
        print('Optimization was stopped with status %d' % status)

    result = ResultSchedMachine(model)
    return result


def solve_instance(machine, df_parts_for_machine, input_dfs):
    """
    :param machine:
    :param unique_machine_id: unique machine / each machine has a unique id, and a site-machine id
    :param df_parts_for_machine: this is the set of parts which are allocated to the machine
    :param input_dfs:
    :return: a dictionary with bid of machine to bundle
    """

    if len(df_parts_for_machine) > 0:
        parameters_model = ParametersMachine(df_parts_for_machine, input_dfs, machine)
        result = solve_LP(parameters_model)
    else:
        result = ResultSchedMachine()

    result.set_location(machine.location)
    result.set_unique_machine_id(machine.unique_machine_id)
    result.set_machine_id(machine.site_machine_id)

    return result
