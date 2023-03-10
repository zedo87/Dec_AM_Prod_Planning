import pandas as pd
from Bidding.Bids import Bids
from Input.parts import Parts


class Results(Parts, Bids):
    def __init__(self, case_id, case_name):
        super().__init__()
        self.result_df = pd.DataFrame()
        self.df_parts = pd.DataFrame()
        self.df_bids = pd.DataFrame()
        self.unique_machine_ids = []
        self.columns = ['SUM', 'SUM_SOLV', 'PROD', 'TRANS', 'SET', 'INV', 'unique_machine_id', 'location']
        self.case_name = case_name
        self.case_id = case_id
        self.last_iteration_ix = 0


    def add_initial_result_of_machine(self, result):
        """
        creates the vcg costs and payments df for the initial state, in which they are all zeros
        (initial state is the inital production plan)
        :param dict_cost_machine:
        :return:
        """
        df_initial_state = pd.Series(result.costs.copy()).to_frame().T
        df_initial_state.loc[:, 'costs_to_pay_vcg'] = 0.0
        df_initial_state.loc[:, 'payments_received_vcg'] = 0.0
        df_initial_state.loc[:, 'payments_received_vcg'] = 0.0
        df_initial_state.loc[:, 'mode'] = 'initial'
        df_initial_state.loc[:, 'cost_saving_vcg'] = 0.0
        df_initial_state.loc[:, 'successful'] = False
        self.result_df = pd.concat([df_initial_state, self.result_df], ignore_index=True)

    def set_reduced_state_of_machines(self):
        """
        reduced state is the initial state, without the requested parts, which are forwarded to the auctioneer
        :return: 
        """
        for unique_machine_id in self.unique_machine_ids:
            df_reduced_state_machine = self.df_bids[(self.df_bids['unique_machine_id'] == unique_machine_id) &
                                                    (self.df_bids['bundle_id'] == -2.0)]\
                                                    [self.columns].copy()
            df_reduced_state_machine.loc[:, 'costs_to_pay_vcg'] = 0.0
            df_reduced_state_machine.loc[:, 'payments_received_vcg'] = 0.0
            df_reduced_state_machine.loc[:, 'payments_received_vcg'] = 0.0
            df_reduced_state_machine.loc[:, 'mode'] = 'reduced'
            df_reduced_state_machine.loc[:, 'cost_saving_vcg'] = 0.0
            df_reduced_state_machine.loc[:, 'successful'] = False
            self.result_df = pd.concat([self.result_df, df_reduced_state_machine], ignore_index=True)

    def get_initial_production_costs_of_machine(self, unique_machine_id):
        initial_production_costs = self.result_df[(self.result_df['unique_machine_id'] == unique_machine_id)
                                                & (self.result_df['mode'] == 'initial')]\
                                                  ['SUM'].sum()
        return initial_production_costs

    def get_new_production_costs_of_machine_of_last_iteration(self, unique_machine_id):
        new_production_costs = self.result_df[(self.result_df['unique_machine_id'] == unique_machine_id)
                                            & (self.result_df['mode'] == 'exchange') \
                                            & (self.result_df['iteration_ix'] == self.last_iteration_ix)] \
                                            ['SUM'].sum()
        return new_production_costs

    def get_vcg_payment_received_of_machine_of_last_iteration(self, unique_machine_id):
        vcg_payment = self.result_df[(self.result_df['unique_machine_id'] == unique_machine_id)
                                   & (self.result_df['mode'] == 'exchange') \
                                   & (self.result_df['iteration_ix'] == self.last_iteration_ix)] \
                                   ['payments_received_vcg'].iloc[0]
        return vcg_payment

    def get_vcg_costs_received_of_machine_of_last_iteration(self, unique_machine_id):
        vcg_costs = self.result_df[(self.result_df['unique_machine_id'] == unique_machine_id)
                                 & (self.result_df['mode'] == 'exchange') \
                                 & (self.result_df['iteration_ix'] == self.last_iteration_ix)] \
                                 ['costs_to_pay_vcg'].iloc[0]
        return vcg_costs

    def get_machines_with_negative_savings_in_last_iteration(self):
        unique_machine_ids = self.result_df['unique_machine_id'].unique().tolist()
        unique_machine_ids_with_neg_costs_savings = []
        for unique_machine_id in unique_machine_ids:
            cost_savings = self.result_df[(self.result_df['unique_machine_id'] == unique_machine_id)
                                     & (self.result_df['mode'] == "exchange")
                                     & (self.result_df['iteration_ix'] == self.last_iteration_ix)
                                     ]["cost_saving_vcg"].sum()
            if cost_savings < -0.1:
                unique_machine_ids_with_neg_costs_savings.append(unique_machine_id)
        return unique_machine_ids_with_neg_costs_savings

    def get_result_df_of_last_iteration_exchange(self):
        result_df = self.result_df[(self.result_df['iteration_ix'] == self.last_iteration_ix)
                                 & (self.result_df['mode'] == 'exchange')]\
                            [['case_name',
                              'iteration_ix',
                              'mode',
                              'successful',
                              'SUM',
                              'SUM_SOLV',
                              'PROD',
                              'TRANS',
                              'INV',
                              'SET',
                              'location',
                              'unique_machine_id',
                              'payments_received_vcg',
                              'costs_to_pay_vcg',
                              'cost_saving_vcg',
                              'bundle_id']].copy()
        return result_df

    def get_result_df(self):
        result_df = self.result_df\
                            [['case_name',
                              'iteration_ix',
                              'mode',
                              'successful',
                              'SUM',
                              'SUM_SOLV',
                              'PROD',
                              'TRANS',
                              'INV',
                              'SET',
                              'location',
                              'unique_machine_id',
                              'payments_received_vcg',
                              'costs_to_pay_vcg',
                              'cost_saving_vcg',
                              'bundle_id']].copy()
        return result_df

    def get_sum_cost_savings_last_iteration(self):
        cost_savings = self.result_df[self.result_df['iteration_ix'] == self.last_iteration_ix]['cost_saving_vcg'].sum()
        return cost_savings

    def set_costs_to_pay_for_machines(self):
        for unique_machine_id in self.unique_machine_ids:
            df_new_state_machine = self.df_bids[(self.df_bids['unique_machine_id'] == unique_machine_id)
                                              & (self.df_bids['winning_bid'] == True)]\
                                                [self.columns].copy()
            costs_to_pay_vcg = self.get_df_parts_of_machine(unique_machine_id)['payment_vcg'].sum()
            costs_to_pay_vcg += self.get_df_parts_of_machine(unique_machine_id)['transport_costs'].sum()
            df_new_state_machine.loc[:, 'costs_to_pay_vcg'] = costs_to_pay_vcg
            df_new_state_machine.loc[:, 'mode'] = 'exchange'
            self.result_df = pd.concat([self.result_df, df_new_state_machine], ignore_index=True)

    def set_payments_received_for_machines_of_last_iteration(self):
        """
        determines the payment for each machine and writes them on result_df. Transport costs can be directly allocated,
        hence they were deducted beforehand, now they must be added again.
        :return:
        """
        for unique_machine_id in self.unique_machine_ids:
            payments_received_vcg = self.get_reassigned_df_parts_of_machine(unique_machine_id)['transport_costs'].sum()
            payments_received_vcg += self.get_reassigned_df_parts_of_machine(unique_machine_id)['payment_vcg'].sum()
            loc_machine_id = (self.result_df['unique_machine_id'] == unique_machine_id) \
                           & (self.result_df['mode'] == 'exchange') \
                           & (self.result_df['iteration_ix'] == self.last_iteration_ix)
            self.result_df.loc[loc_machine_id, 'payments_received_vcg'] = payments_received_vcg

    def set_optimization_succesful_in_last_iteration(self, successful):
        self.result_df.loc[(self.result_df['iteration_ix'] == self.last_iteration_ix)
                         & (self.result_df['mode'] == 'exchange'), 'successful'] = successful

    def set_cost_savings_for_machines_of_last_iteration(self):
        for unique_machine_id in self.unique_machine_ids:
            cost_saving = self.get_initial_production_costs_of_machine(unique_machine_id) \
                          - self.get_new_production_costs_of_machine_of_last_iteration(unique_machine_id) \
                          + self.get_vcg_payment_received_of_machine_of_last_iteration(unique_machine_id) \
                          - self.get_vcg_costs_received_of_machine_of_last_iteration(unique_machine_id)
            self.result_df.loc[(self.result_df['unique_machine_id'] == unique_machine_id)
                             & (self.result_df['mode'] == 'exchange') \
                             & (self.result_df['iteration_ix'] == self.last_iteration_ix), 'cost_saving_vcg'] \
                    = cost_saving

    def set_number_of_parts_initial_for_machines(self):
        for unique_machine_id in self.unique_machine_ids:
            number_of_parts_initial_state = len(self.get_part_list_of_unique_machine_id(unique_machine_id))
            self.result_df.loc[(self.result_df['unique_machine_id'] == unique_machine_id)
                             & (self.result_df['mode'] == 'initial') \
                             & (self.result_df['iteration_ix'] == self.last_iteration_ix), 'number_of_parts'] \
                    = number_of_parts_initial_state

    def set_number_of_parts_reassigned_plan_for_machine(self):
        for unique_machine_id in self.unique_machine_ids:
            number_of_parts_reassigned_state = len(self.get_reassigned_df_parts_of_machine(unique_machine_id))
            self.result_df.loc[(self.result_df['unique_machine_id'] == unique_machine_id)
                             & (self.result_df['mode'] == 'exchange') \
                             & (self.result_df['iteration_ix'] == self.last_iteration_ix), 'number_of_parts'] \
                                = number_of_parts_reassigned_state

    def set_number_of_requested_parts_for_machine(self):
        for unique_machine_id in self.unique_machine_ids:
            parts_requested = len(self.get_df_parts_of_requested_parts_of_machine(unique_machine_id))
            self.result_df.loc[(self.result_df['unique_machine_id'] == unique_machine_id)
                             & (self.result_df['mode'] == 'exchange')\
                             & (self.result_df['iteration_ix'] == self.last_iteration_ix), 'parts_requested'] \
                             = parts_requested

    def set_number_of_parts_received_wo_own_parts(self):
        for unique_machine_id in self.unique_machine_ids:
            parts_received_without_own_parts = len(self.df_parts[
                                                       (self.df_parts['unique_machine_id_new'] == unique_machine_id)
                                                       & (self.df_parts['unique_machine_id'] != unique_machine_id)])
            self.result_df.loc[(self.result_df['unique_machine_id'] == unique_machine_id)
                               & (self.result_df['mode'] == 'exchange')
                               & (self.result_df['iteration_ix'] == self.last_iteration_ix),
                                'parts_received_without_own_parts'] = parts_received_without_own_parts

    def set_number_of_parts_received_with_own_parts(self):
        for unique_machine_id in self.unique_machine_ids:
            parts_received_with_own_parts = len(self.get_reassigned_df_parts_of_machine(unique_machine_id))
            self.result_df.loc[(self.result_df['unique_machine_id'] == unique_machine_id)
                         & (self.result_df['mode'] == 'exchange')
                         & (self.result_df['iteration_ix'] == self.last_iteration_ix), 'parts_received_with_own_parts'] \
                         = parts_received_with_own_parts

    def set_bundle_received(self):
        for unique_machine_id in self.unique_machine_ids:
            winning_bundle_id = self.get_winning_bundle_of_machine(unique_machine_id)
            self.result_df.loc[(self.result_df['unique_machine_id'] == unique_machine_id)
                               & (self.result_df['mode'] == 'exchange')
                               & (self.result_df['iteration_ix'] == self.last_iteration_ix), 'bundle_id'] \
                               = winning_bundle_id

    def get_sum_of_costs_of_last_iteration(self):
        df_result_last_it = self.get_result_df_of_last_iteration_exchange()
        sr_result = df_result_last_it[['SUM', 'SUM_SOLV', 'PROD', 'TRANS', 'SET', 'INV']].sum(axis=0)
        return sr_result

    def get_sum_of_initial_cost(self):
        sr_result = self.result_df[self.result_df['mode'] == 'initial'] \
                        [['SUM',
                          'SUM_SOLV',
                          'PROD',
                          'TRANS',
                          'INV',
                          'SET']].sum(axis=0)
        return sr_result

    def set_number_of_parts_of_last_iteration(self):
        self.set_number_of_parts_initial_for_machines()
        self.set_number_of_parts_reassigned_plan_for_machine()
        self.set_number_of_requested_parts_for_machine()
        self.set_number_of_parts_received_wo_own_parts()
        self.set_number_of_parts_received_with_own_parts()

    def set_iteration_index(self, iteration_index):
        self.result_df.loc[:, 'iteration'] = iteration_index

    def set_with_withdrawal(self, with_withdrawal):
        self.result_df.loc[:, 'with_withdrawal'] = with_withdrawal

    def set_case_name_and_id(self):
        self.result_df.loc[:, 'case_id'] = self.case_id
        self.result_df.loc[:, 'case_name'] = self.case_name

    def set_last_iteration_ix(self):
        self.last_iteration_ix = self.result_df['iteration_ix'].max()

    def set_iteration_to_results_df(self):
        try:
            self.result_df.loc[self.result_df['iteration_ix'].isnull(), 'iteration_ix'] = self.last_iteration_ix + 1
        except KeyError:
            self.result_df.loc[:, 'iteration_ix'] = 1
        self.set_last_iteration_ix()

    def add_reassigned_results(self, parts, bids):
        """
        :return: creates the result df in which the most important key figures are represented for each machine
        key figures are:
            - initial production costs
            - new production costs
            - payments to auctioneer
            - payments received from auctioneer
            - savings for each machine
        """
        self.df_bids = bids.df_bids.copy()
        self.df_parts = parts.df_parts.copy()

        if self.last_iteration_ix == 0:
            self.set_reduced_state_of_machines()
            self.unique_machine_ids = self.get_unique_machine_ids()

        self.set_costs_to_pay_for_machines()
        self.set_iteration_to_results_df()
        self.set_payments_received_for_machines_of_last_iteration()
        self.set_cost_savings_for_machines_of_last_iteration()
        self.set_number_of_parts_of_last_iteration()
        self.set_bundle_received()
        self.set_case_name_and_id()





