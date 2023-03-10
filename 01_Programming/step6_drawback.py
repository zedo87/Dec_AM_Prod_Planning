




def individual_rationality(parts, results, iteration_index):
    """
    this method checks if the framework was succesful, but also if the result of this iteration should be added to
    the overall result df.
    :param result_df:
    :param df_parts_scheduled:
    :param iteration_index:
    :return:
    """
    print("--------- Step 6 - Drawback ---------")
    machines_with_negative_savings = results.get_machines_with_negative_savings_in_last_iteration()
    another_iteration_necessary = True
    if len(machines_with_negative_savings) == 0 \
            or iteration_index == 0 \
            or iteration_index >= 10:

        if len(machines_with_negative_savings) == 0:
            results.set_optimization_succesful_in_last_iteration(True)
            another_iteration_necessary = False
        else:
            results.set_optimization_succesful_in_last_iteration(False)
        if iteration_index == 0:
            results.set_with_withdrawal(False)
        else:
            results.set_with_withdrawal(True)
        if iteration_index >= 10:
            another_iteration_necessary = False

    parts.reset_request_parts_of_machines(machines_with_negative_savings)
    parts.drop_payment_columns()

    if len(parts.get_df_of_requested_parts()) == 0:
        another_iteration_necessary = False

    else:
        if len(machines_with_negative_savings) > 0:
            print("Machine list with negative savings:")
            print(machines_with_negative_savings)
            print("Iteration for this case necessary! Iteration number %s start" % iteration_index)

    if (another_iteration_necessary == False) & \
        ((results.get_sum_cost_savings_last_iteration() < 0.1) | len(machines_with_negative_savings) > 0):
        print("No better solution found - use initial allocation.")

    return another_iteration_necessary

