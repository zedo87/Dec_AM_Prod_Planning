import pandas as pd
import mysql.connector as connector
from sklearn.ensemble import RandomForestRegressor

class Predictor:
    def __init__(self):
        self.columns = ['result_id',
                   'scenario_id',
                   'solver_successful',
                   'transport_costs',
                   'inventory_costs',
                   'production_costs',
                   'setup_costs',
                   'total_costs',
                   'total_costs_wo_trans',
                   'duration_sec',
                   'acc_height',
                   'min_height',
                   'max_height',
                   'std_height',
                   'acc_length',
                   'min_length',
                   'max_length',
                   'std_length',
                   'acc_width',
                   'min_width',
                   'max_width',
                   'std_width',
                   'acc_area',
                   'min_area',
                   'max_area',
                   'std_area',
                   'acc_volume',
                   'min_volume',
                   'max_volume',
                   'std_volume',
                   'acc_due_date',
                   'min_due_date',
                   'max_due_date',
                   'std_due_date',
                   'n_materials',
                   'n_parts']
        self.connection = None
        self.cursor = None
        self.connect()
        self.train_model()

    def create_key_features(self, df_parts, attribute):
        """
        Input: df_parts: Dataframe, attribute_string e.g.[height, volume, width,...]
        Output: dict_key_features, with sum. min max and std values of feature
        """
        dict_key_feature = {'acc_' + attribute: df_parts[attribute].sum(),
                            'min_' + attribute: df_parts[attribute].min(),
                            'max_' + attribute: df_parts[attribute].max()}

        if len(df_parts) >= 2:
            dict_key_feature['std_' + attribute] = df_parts[attribute].std()
        else:
            dict_key_feature['std_' + attribute] = 0

        return dict_key_feature

    def calculate_transport_costs(self, df_parts, machine, input_dfs):
        origin = machine['location']
        transport_costs = 0
        for part in df_parts.iterrows():
            price = part[1]['price']
            destination = part[1]['destination']
            transport_duration = \
                float(input_dfs.df_transport[input_dfs.df_transport['destination'] == origin][destination]) * 24
            transport_costs += float(price * float(input_dfs.sr_parameters['psi'])
                                     + float(input_dfs.sr_parameters['omega']) * transport_duration)
        return transport_costs

    def connect(self):
        self.connection = connector.connect(host='localhost',
                                       database='collab_am',
                                       user='dozehetner',
                                       password='IbaO,ysub2nGg.',
                                       port=3306)
        if self.connection.is_connected():
            db_Info = self.connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            self.cursor = self.connection.cursor()
            self.cursor.execute("select database();")
            record = self.cursor.fetchone()
            print("You're connected to database: ", record)

    def get_all_costs_and_features(self, resultID=None):
        cursor = self.connection.cursor(dictionary=True)
        if resultID is None:
            query = """SELECT results.*, features.* FROM results
                JOIN features ON results.result_id=features.result_id;"""
        else:
            query = """SELECT results.*, features.* 
                    FROM results
                    JOIN features ON results.result_id=features.result_id
                    WHERE results.result_id = """ + str(resultID) + ";"
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame()
        for i in range(len(data)):
            row = pd.DataFrame(data[i], index=[i])
            df = pd.concat([df, row], ignore_index=True)
        return df

    def get_all_resultIDs(self):
        query = "SELECT resultID FROM results;"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        list_resultIDs = []
        for row in data:
            list_resultIDs.append(row[0])
        return list_resultIDs

    def train_model(self):
        dataset = self.get_all_costs_and_features()
        dataset['total_costs_wo_trans'] = dataset['total_costs'] - dataset['transport_costs']
        dataset = dataset.groupby('total_costs_wo_trans').head(1) # to remove duplicates-> FIX IT LATER in SQL DB

        dataset = dataset[self.columns]
        X = dataset.iloc[:, 10:]
        y = dataset.iloc[:, 8]
        self.model = RandomForestRegressor()
        self.model.fit(X, y)

    def predict_costs(self, df_parts, machine, input_dfs):
        """Input: df_parts for part feature, machine for calculating transportation costs,
        Output: estimated costs in €"""
        if len(df_parts) > 0:
            df_parts_analysis = df_parts.copy()
            df_parts_analysis.loc[:, 'area'] = df_parts_analysis['area'] / 10.0
            df_parts_analysis.loc[:, 'volume'] = df_parts_analysis['height'] \
                                                 * df_parts_analysis['width'] \
                                                 * df_parts_analysis['length'] \
                                                 / 10000.0

            for part in df_parts.iterrows():
                df_parts_analysis.loc[part[0], 'due_date'] = part[1]['due_date'].timestamp()

            sr_features = pd.concat([
                pd.Series(self.create_key_features(df_parts_analysis, 'height')),
                pd.Series(self.create_key_features(df_parts_analysis, 'width')),
                pd.Series(self.create_key_features(df_parts_analysis, 'length')),
                pd.Series(self.create_key_features(df_parts_analysis, 'area')),
                pd.Series(self.create_key_features(df_parts_analysis, 'volume')),
                pd.Series(self.create_key_features(df_parts_analysis, 'due_date')),
                pd.Series({'n_materials': len(df_parts_analysis['material_id'].unique())}),
                pd.Series({'n_parts': len(df_parts_analysis)})])

            transport_costs = self.calculate_transport_costs(df_parts_analysis, machine, input_dfs)
            X = sr_features.to_frame().T
            other_costs = self.apply_model_for_prediction(X)[0]
            if other_costs < 0:
                other_costs = 0
            costs = transport_costs + other_costs
        else:
            other_costs = 0
            costs = 0
            transport_costs = 0

        dict_costs = {
            'SUM': costs,
            'TRANS': transport_costs,
            'OTH': other_costs,
            'site': machine['location'],
            'machine_id': machine.site_machine_id,
            'unique_machine_id': machine.unique_machine_id}
        return dict_costs

    def apply_model_for_prediction(self, X):
        """Input: Pandas series with required features]
        Output: y -> estimated production costs + setup costs + inventory costs"""
        y = self.model.predict(X[self.columns[10:]])
        return y
