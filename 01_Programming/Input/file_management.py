import pandas as pd


class InputDataFrames:
    def __init__(self, filename=None, df_parts=None, df_sites=None, df_transport=None, parameters=None):
        if filename:
            self.df_parts, self.df_sites, self.df_transport, self.sr_parameters = read_files(filename)
        else:
            self.df_parts = df_parts
            self.df_sites = df_sites
            self.df_transport = df_transport
            self.sr_parameters = parameters
        self.df_machines = pd.DataFrame()
        self.create_machine_df()

    def get_machine_with_unique_machine_id(self, unique_machine_id):
        machine = self.df_machines[self.df_machines['unique_machine_id'] == unique_machine_id].iloc[0]
        return machine

    def set_scenario_id_to_dfs(self, scenario_id):
        try:
            self.df_parts.loc[:, 'scenario_id'] = scenario_id
        except ValueError:
            print("Help")
        self.df_sites.loc[:, 'scenario_id'] = scenario_id
        self.df_transport.loc[:, 'scenario_id'] = scenario_id
        self.sr_parameters['scenario_id'] = scenario_id

    def set_unique_part_id(self):
        self.df_parts['unique_part_id'] = self.df_parts['scenario_id'] + '_' + self.df_parts['part_id'].astype(str)

    def create_machine_df(self):
        """
        input: ordered df_sites
        output: df_machines with unique_machine_ids
        """
        unique_machine_id = 0
        for index, site in self.df_sites.iterrows():
            machine_id = 0
            for i in range(site['number_of_machines']):
                sr_machine = pd.Series({
                    'unique_machine_id': unique_machine_id,
                    'site_machine_id': machine_id,
                    'location': site['location']})
                self.df_machines = pd.concat([self.df_machines, sr_machine.to_frame().T], ignore_index=True)
                unique_machine_id += 1
                machine_id += 1
        self.df_machines = pd.merge(self.df_machines, self.df_sites, on='location')


def read_files(filename):
    file_name_input_data = filename

    df_parts = pd.read_excel(file_name_input_data, sheet_name='Parts')
    df_sites = pd.read_excel(file_name_input_data, sheet_name='Site')

    df_transport = pd.read_excel(file_name_input_data, sheet_name='Transport') \
        .drop(columns="Unnamed: 0")

    df_parameters = pd.read_excel(file_name_input_data, sheet_name="Parameters")
    parameters = df_parameters.iloc[0]
    df_parts.loc[:, "area"] = df_parts["width" ] * df_parts["length"]
    df_parts = df_parts.rename(columns={'Unnamed: 0': 'part_id',
                                        'material': 'material_id'})

    df_sites = df_sites.rename(columns={'destination': 'location',
                                        'Site_number': 'site_id'})
    df_transport = df_transport.rename(columns={'Destination': 'destination'})

    #"""HACK!!!!!!!!!!!!!!!!!!"""
    df_parts_hack = pd.DataFrame()
    for origin in df_parts['origin'].unique().tolist():
        df_parts_hack = pd.concat([df_parts_hack, df_parts[df_parts['origin'] == origin].iloc[:10]], ignore_index=True)
    df_parts = df_parts_hack
    return df_parts, df_sites, df_transport, parameters


def get_old_results(output_file_path_result, path_output_computational_time):
    try:
        overall_result_df = pd.read_excel(output_file_path_result, index_col="Unnamed: 0")
    except FileNotFoundError:
        overall_result_df = pd.DataFrame()
    try:
        overall_computational_df = pd.read_excel(path_output_computational_time, index_col="Unnamed: 0")
    except FileNotFoundError:
        overall_computational_df = pd.DataFrame()
    return overall_result_df, overall_computational_df
