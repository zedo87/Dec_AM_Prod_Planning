import pandas as pd


class Parts:
    def __init__(self, df_parts=pd.DataFrame(), **kw):
        self.df_parts = df_parts.copy()

    def get_all_unique_machine_ids(self):
        unique_machine_ids = self.df_parts['unique_machine_id'].unique().tolist()
        return unique_machine_ids

    def get_are_parts_with_requests_available(self):
        """checks if there are parts with request available
        return: Bool -> True if there are still parts"""
        parts_available = len(self.df_parts[self.df_parts['request_part'] == True]) > 0
        return parts_available

    def get_df_of_requested_parts(self):
        return self.df_parts[self.df_parts['request_part'] == True].copy()

    def get_part_list_of_unique_machine_id(self, unique_machine_id):
        parts = self.df_parts[self.df_parts['unique_machine_id'] == unique_machine_id]['part_id'].to_list()
        return parts

    def get_df_parts_of_machine_wo_request(self, unique_machine_id):
        df_parts = self.df_parts[(self.df_parts['unique_machine_id'] == unique_machine_id) & \
                                 (self.df_parts["request_part"] != True)].copy()
        return df_parts

    def get_df_parts_of_requested_parts_of_machine(self, unique_machine_id):
        df_parts = self.df_parts[(self.df_parts['unique_machine_id'] == unique_machine_id) & \
                                 (self.df_parts['request_part'] == True)].copy()
        return df_parts

    def get_df_parts_of_machine(self, unique_machine_id):
        df_parts = self.df_parts[(self.df_parts['unique_machine_id'] == unique_machine_id)].copy()
        return df_parts

    def get_reassigned_df_parts_of_machine(self, unique_machine_id):
        df_parts = self.df_parts[(self.df_parts['unique_machine_id_new'] == unique_machine_id)].copy()
        return df_parts

    def get_df_parts_of_part_list(self, part_list):
        return self.df_parts[self.df_parts['part_id'].isin(part_list)]

    def set_Shapley_costs_to_parts(self, df_margin):
        for row in df_margin.iterrows():
            costs = row[1]['marginal_costs']
            part_id = row[1]['part_id']
            unique_machine_id = row[1]['unique_machine_id']
            self.df_parts.loc[(self.df_parts['unique_machine_id'] == unique_machine_id) &
                              (self.df_parts['part_id'] == part_id), 'shapley_cost'] = costs

    def set_margin_to_parts(self):
        self.df_parts['margin'] = 1 - self.df_parts['shapley_cost'] / self.df_parts['price']

    def reset_request_parts_of_machines(self, list_of_machines):
        self.df_parts.loc[self.df_parts['unique_machine_id'].isin(list_of_machines), 'request_part'] = False

    def drop_payment_columns(self):
        self.df_parts = self.df_parts.drop(columns=['payment_vcg_wo_TRANS',
                                                    'transport_costs',
                                                    'payment_vcg',
                                                    'unique_machine_id_new',
                                                    'bundle_id',
                                                    'new_origin'])


    def set_flag_parts_for_request(self, margin_limit):
        self.df_parts['request_part'] = self.df_parts['margin'] < margin_limit

    def get_df_parts(self):
        return self.df_parts.copy()


    def set_payments(self, df_payments):
        for part in df_payments.iterrows():
            part_id = part[1]['part_id']
            part_index = self.df_parts[self.df_parts['part_id'] == part_id].index.values[0]

            self.df_parts.loc[part_index, 'payment_vcg_wo_TRANS'] = part[1]['payment_vcg_wo_TRANS']
            self.df_parts.loc[part_index, 'transport_costs'] = part[1]['transport_costs']
            self.df_parts.loc[part_index, 'payment_vcg'] = part[1]['payment_vcg_wo_TRANS'] \
                                                         + part[1]['transport_costs']
            self.df_parts.loc[part_index, 'unique_machine_id_new'] = part[1]['unique_machine_id_new']
            self.df_parts.loc[part_index, 'bundle_id'] = part[1]['bundle_id']
            self.df_parts.loc[part_index, 'new_origin'] = part[1]['new_origin']

    def set_unique_machine_id(self, input_dfs):
        self.df_parts = pd.merge(self.df_parts,
                                 input_dfs.df_machines[['site_id', 'site_machine_id', 'unique_machine_id']],
                                 on=['site_id', 'site_machine_id'])


