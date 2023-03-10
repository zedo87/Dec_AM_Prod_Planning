import pandas as pd


class Bundles:
    def __init__(self, df_bundles=pd.DataFrame()):
        self.df_bundles = df_bundles

    def create_initial_bundle(self, df_parts):
        self.df_bundles = pd.DataFrame()
        P = df_parts.index.to_list()
        for p in P:
            series_bundle = pd.Series({'part_ids':[df_parts.loc[p]["part_id"]], 'level': 0})
            self.df_bundles = pd.concat([self.df_bundles, series_bundle.to_frame().T], ignore_index=True)

    def add_bundle_to_overall_df(self, df_bundle):
        self.df_bundles = pd.concat([self.df_bundles, df_bundle], ignore_index=True)

    def get_highest_level_of_bundles(self):
        return self.df_bundles['level'].max()

    def reindex_bundles(self):
        self.df_bundles.index = range(len(self.df_bundles))

    def get_parts_of_bundle(self, bundle_id):
        """
        return part list from bundle df. if bundle_id <0 -> return empty list. this is important for bundles with index
        -1 and -2
        :param bundle_id:
        :return:
        """
        if bundle_id < 0:
            part_list = []
        else:
            part_list = self.df_bundles.loc[bundle_id]['part_ids']
        return part_list

    def set_winning_bid_to_df_bundles(self, bids):
        self.df_bundles.loc[:, 'winning_bid'] = False
        column_index = self.df_bundles.columns.to_list().index('winning_bid')
        for bid in bids.df_bids.iterrows():
            if bid[1]['winning_bid'] == True:
                bundle_index = int(bid[1]['bundle_id'])
                self.df_bundles.iat[bundle_index, column_index] = True

    def get_bundles_of_level(self, level):
        df_bundle = self.df_bundles[self.df_bundles['level'] == level].copy()
        return df_bundle

    def get_indices_of_bundles(self):
        return list(self.df_bundles.index)




