import pandas as pd


class Bids:
    def __init__(self, df_bids=pd.DataFrame(), estimate=False, **kw):
        self.df_bids = df_bids
        self.estimate = estimate

    def compute_marginal_costs(self):
        """
        computes marginal costs for each bid, marginal costs are calculated
        using the production costs of the bundle
        and deducting th costs of bid of bundle -2 (this is the production plan with parts without requested parts)
        the marginal costs are then written on the bids_df in column 'marginal costs'
        :return:
        """
        self.df_bids.loc[:, 'marginal_costs'] = 0.0
        for unique_machine_id in self.df_bids['unique_machine_id'].unique().tolist():
            df_bidding_machine = self.get_bids_to_of_unique_machine(unique_machine_id)
            reference_costs = self.get_initial_costs_wo_any_bundle_of_machine(unique_machine_id)
            for bundle in df_bidding_machine.iterrows():
                if bundle[1]['bundle_id'] != -2: # initial costs excluded
                    costs = bundle[1]['SUM']
                    marginal_costs = costs - reference_costs
                    self.df_bids.at[bundle[0], 'marginal_costs'] = float(marginal_costs)
        return self.df_bids

    def set_flag_winning_bid(self, W_bi):
        """
        uses W_bi to set winning bid flag in df_bid.
        :param W_bi: winner matrix of LP
        :return: creates and determines the column 'winning bid' in the df_bids
        """
        self.df_bids.loc[:, 'winning_bid'] = False
        for row in self.df_bids.iterrows():
            b = row[1]['bundle_id']
            i = row[1]['unique_machine_id']
            if W_bi.get((b, i), 0) == 1:
                self.df_bids.loc[(self.df_bids['unique_machine_id'] == i) & \
                                 (self.df_bids['bundle_id'] == b), 'winning_bid'] = True

        for unique_machine in self.df_bids['unique_machine_id'].unique().tolist():
            if self.df_bids[self.df_bids['unique_machine_id'] == unique_machine]['winning_bid'].sum() == 0:
                self.df_bids.loc[(self.df_bids['unique_machine_id'] == unique_machine) & \
                                 (self.df_bids['bundle_id'] == -2), 'winning_bid'] = True

    def reset_flags_winning_bid(self):
        self.df_bids.loc[:, 'winning_bid'] = False

    def set_flag_promising_machines_for_bundle(self, number_of_machines):
        """
        Selects the n (number of machines) lowest bids for each bundles, and flags it with "request_true_bid" in the
        dataframe. Also flags, -1 (parts without request) and -2 bundles (bundle with request parts),
        as they are required for the WDP
        :param df_bidding_estimate: bidding df, which contains the predicted bids for each bundle for each machine
        :param number_of_machines: the number of x lowest bids which are the selected for a "True" bid
        :return: df_bidding_estimate enriched with colum 'request_true_bid'
        """
        self.df_bids.loc[:, 'request_true_bid'] = False
        for bundle in self.df_bids['bundle_id'].unique().tolist():
            if bundle != -2:
                df_bids_for_bundle = self.df_bids[self.df_bids['bundle_id'] == bundle]
                best_machines = df_bids_for_bundle.sort_values('marginal_costs')['unique_machine_id'].to_list()[:number_of_machines]
                self.df_bids.loc[((self.df_bids['unique_machine_id'].isin(best_machines))
                                                & (self.df_bids['bundle_id'] == bundle)), 'request_true_bid'] = True

        self.df_bids.loc[self.df_bids['bundle_id'] == -2, 'request_true_bid'] = True

    def add_bids_to_overall_df_bid(self, df_bid):
        self.df_bids = pd.concat([self.df_bids, df_bid.copy()], ignore_index=True)

    def get_bids_to_of_unique_machine(self, unique_machine_id):
        df_bids = self.df_bids[self.df_bids['unique_machine_id'] == unique_machine_id].copy()
        return df_bids

    def set_payment(self, p_i):
        unique_machine_ids = p_i.keys()
        self.df_bids.loc[:, 'payment'] = 0
        for unique_machine_id in unique_machine_ids:
            self.df_bids.loc[(self.df_bids.unique_machine_id == unique_machine_id) & (
                    self.df_bids.winning_bid == True), 'payment'] = p_i[unique_machine_id]

    def get_unique_machine_ids(self):
        return self.df_bids['unique_machine_id'].unique().tolist()

    def get_initial_costs_wo_any_bundle_of_machine(self, unique_machine_id):
        df_biding_machine = self.get_bids_to_of_unique_machine(unique_machine_id)
        costs = df_biding_machine.loc[df_biding_machine["bundle_id"] == -2]["SUM"].iloc[0]
        return costs

    def get_winning_bid_value_of_machine(self, unique_machine_id):
        value_bid = self.df_bids[(self.df_bids['unique_machine_id'] == unique_machine_id) \
                                 & (self.df_bids['winning_bid'] == True)]['marginal_costs'].sum()
        return value_bid

    def get_winning_bundle_of_machine(self, unique_machine_id):
        bundle_id = self.df_bids[(self.df_bids['unique_machine_id'] == unique_machine_id) \
                                 & (self.df_bids['winning_bid'] == True)]['bundle_id'].iloc[0]
        return bundle_id

    def get_revenue_of_auction(self):
        return self.df_bids[self.df_bids["winning_bid"] == True]["marginal_costs"].sum()
